from datetime import date
from unittest.mock import patch
from django.test import TestCase,SimpleTestCase,override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Activity,Kudos
from .gpx import parse,InvalidGPX,distance
from .demo import sample_gpx
from .tasks import process_activity
class GPXTests(SimpleTestCase):
    def test_known_distance(self):self.assertAlmostEqual(distance((0,0),(0,1)),111194.93,places=1)
    def test_valid_loop_and_elapsed_pace(self):
        result=parse(sample_gpx());self.assertTrue(6000<result['distance']<7000);self.assertEqual(result['duration'],2160);self.assertAlmostEqual(result['elevation'],40,delta=1);self.assertTrue(len(result['route'])<=501)
    def test_xml_entities_are_blocked(self):
        with self.assertRaises(InvalidGPX):parse(b'<!DOCTYPE gpx [<!ENTITY x SYSTEM "file:///etc/passwd">]><gpx>&x;</gpx>')
    def test_coordinate_time_and_size_validation(self):
        bad=[b'<gpx/>',b'not xml',sample_gpx().replace(b'37.770000',b'97.770000'),sample_gpx().replace(b'07:00:12',b'06:00:12'),b'x'*2_000_001,sample_gpx().replace(b'<time>',b'<other>').replace(b'</time>',b'</other>')]
        for raw in bad:
            with self.subTest(size=len(raw)),self.assertRaises(InvalidGPX):parse(raw)
    def test_segments_do_not_create_false_distance(self):
        xml=b'<gpx><trk><trkseg><trkpt lat="0" lon="0"><time>2026-01-01T00:00:00Z</time></trkpt><trkpt lat="0" lon="0.01"><time>2026-01-01T00:01:00Z</time></trkpt></trkseg><trkseg><trkpt lat="50" lon="50"><time>2026-01-01T00:02:00Z</time></trkpt><trkpt lat="50" lon="50.01"><time>2026-01-01T00:03:00Z</time></trkpt></trkseg></trk></gpx>'
        result=parse(xml);self.assertTrue(result['distance']<2000);self.assertEqual(result['duration'],120)
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class ActivityTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user('alice',password='test-password');self.other=get_user_model().objects.create_user('bob',password='test-password');self.client.force_login(self.user)
    def activity(self,public=False):
        a=Activity.objects.create(user=self.user,title='Morning loop',sport='run',date=date.today(),public=public,gpx=sample_gpx());process_activity(a.pk);a.refresh_from_db();return a
    def test_worker_is_idempotent_and_page_renders(self):
        a=self.activity();process_activity(a.pk);a.refresh_from_db();self.assertEqual(a.status,'ready');self.assertEqual(len(a.route),181)
        for path in ['/','/new/',f'/activities/{a.pk}/',f'/activities/{a.pk}/download/']:self.assertEqual(self.client.get(path).status_code,200)
    def test_upload_runs_processing(self):
        response=self.client.post('/new/',{'title':'Trail run','sport':'run','date':str(date.today()),'file':SimpleUploadedFile('track.gpx',sample_gpx())});self.assertEqual(response.status_code,302);self.assertEqual(Activity.objects.get().status,'ready')
    def test_private_route_and_mutations(self):
        a=self.activity();self.client.force_login(self.other)
        for suffix in ['','download/']:self.assertEqual(self.client.get(f'/activities/{a.pk}/{suffix}').status_code,404)
        for suffix in ['kudos/','comment/','delete/','visibility/','retry/']:self.assertEqual(self.client.post(f'/activities/{a.pk}/{suffix}',{'text':'hello'}).status_code,404)
        self.assertNotContains(self.client.get('/'),'Morning loop')
    def test_public_social_and_owner_protection(self):
        a=self.activity(public=True);self.client.force_login(self.other)
        self.assertEqual(self.client.get(f'/activities/{a.pk}/').status_code,200)
        for _ in range(2):self.client.post(f'/activities/{a.pk}/kudos/')
        self.assertEqual(Kudos.objects.count(),1)
        self.client.post(f'/activities/{a.pk}/comment/',{'text':'<script>alert(1)</script>'});self.assertContains(self.client.get(f'/activities/{a.pk}/'),'&lt;script&gt;')
        self.assertEqual(self.client.post(f'/activities/{a.pk}/delete/').status_code,404)
        self.client.force_login(self.user);self.client.post(f'/activities/{a.pk}/visibility/');self.client.force_login(self.other);self.assertEqual(self.client.get(f'/activities/{a.pk}/').status_code,404)
    def test_invalid_upload_is_visible_failure(self):
        a=Activity.objects.create(user=self.user,title='Bad file',sport='run',date=date.today(),gpx=b'<gpx/>');process_activity(a.pk);a.refresh_from_db();self.assertEqual(a.status,'failed');self.assertTrue(a.error)
    def test_broker_failure_and_retry(self):
        with patch('app.views.process_activity.delay',side_effect=ConnectionError):self.client.post('/new/',{'title':'Queued','sport':'walk','date':str(date.today()),'file':SimpleUploadedFile('route.gpx',sample_gpx())})
        a=Activity.objects.get();self.assertEqual(a.status,'failed');self.client.post(f'/activities/{a.pk}/retry/');a.refresh_from_db();self.assertEqual(a.status,'ready')
    def test_login_and_csrf_mutations(self):
        a=self.activity();self.assertEqual(self.client.get(f'/activities/{a.pk}/delete/').status_code,405);self.client.logout();self.assertEqual(self.client.get('/').status_code,302)
