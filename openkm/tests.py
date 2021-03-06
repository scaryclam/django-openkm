import datetime

from django.test import TestCase
from django.conf import settings

import suds

import client, facades, models, sync, utils


class ClientTest(TestCase):
    """ Tests of functions and settings """

    def setUp(self):
        pass

    def test_settings(self):
        """ Check that the config values are set in the settings file """
        keys = ('Logging', 'UploadRoot', 'Host', 'User', 'Password')
        for key in keys:
            self.assertTrue(settings.OPENKM['configuration'].has_key(key))

    def test_wsdl_map(self):
        """ Check fof the presence of the WSDL dict map """
        self.assertTrue(isinstance(client.OPENKM_WSDLS, dict))


class FolderTest(TestCase):

    def setUp(self):
        self.folder = client.Folder()

    def test_get_children(self):
        children = self.folder.get_children('/okm:root/')
        self.assertTrue(hasattr(children, 'item'))


class AuthTest(TestCase):

    def setUp(self):
        self.auth = client.Auth()

    def test_login(self):
        """ Check we can login and get a token """
        self.auth.login()
        self.assertTrue(hasattr(self.auth, 'token'), msg="Token has not been set")
        self.assertTrue(len(self.auth.token) > 1, msg="Token is empty")

    def test_logout(self):
        """ A successful logout should destroy the session token """
        self.auth.login()
        has_token = hasattr(object, 'token')
        self.auth.logout()

        try:
            # this should fail as now logged out
            has_token = hasattr(object, 'token')
        except AttributeError:
            has_token = False
        finally:
            self.assertFalse(has_token)

    def has_token_attribute(self, object):
        return hasattr(object, 'token')

    def test_get_roles(self):
        self.auth.login()
        roles = self.auth.get_roles()
        self.assertTrue(hasattr(roles, 'item'), msg="instance expected to contain item[]")
        self.assertTrue(isinstance(roles.item, list), msg="role.item expected to be a list")

    def test_grant_role(self):
        pass

    def test_revoke_role(self):
        pass

    def test_get_users(self):
        pass

    def test_grant_user(self):
        pass

    def test_revoke_user(self):
        pass

    def test_get_granted_users(self):
        pass


class DocumentTest(TestCase):

    test_doc_path = '%s%s' % (settings.OPENKM['configuration']['UploadRoot'], 'testing123.pdf')

    def setUp(self):
        try:
            # create a test document
            self.doc = client.Document()
            test_doc = self.doc.new()
            test_doc.path = self.test_doc_path
            self.doc.create(test_doc, "hf7438hf7843h378ot4837ht7")
            self.test_doc = self.doc.get_properties(self.test_doc_path)
        except AssertionError, detail:
            logging.exception(detail)

    def test_token_has_been_set(self):
        """
        Check that the token has been set in both Auth and Document,
        otherwise we won't be doing anything
        """
        self.assertTrue(hasattr(self.doc, 'token'), msg="Token not set in Document")

    def document_object(self, doc):
        """
        Test the structure of a document instance
        """
        keys = ('actualVersion', 'author', 'checkedOut', 'convertibleToDxf',
                'convertibleToPdf', 'convertibleToSwf', 'created', 'language', 'lastModified',
                'locked', 'mimeType', 'path', 'permissions', 'subscribed', 'uuid')
        for key in keys:
            msg = "%s doesn't exist" % key
            self.assertTrue(hasattr(doc, key), msg)

        return True

    def test_create(self):
        """ Create a test document """
        test_doc = self.doc.new()
        filename = 'abc.pdf'
        test_doc.path = '%s%s' % (settings.OPENKM['configuration']['UploadRoot'], filename)
        content = "hf8478y7ro48y7y7t4y78o4"
        self.doc.create(test_doc, content)
        new_document = self.doc.get_properties(test_doc.path)

        self.assertEqual(test_doc.path, new_document.path, msg="Created document path does not match that uploaded")

        # clean up the file, otherwise it will remain on OpenKM causing the next test run to fail
        self.doc.delete(new_document.path)

    def test_lock(self):
        """ Lock and unlock a document """
        self.doc.lock(self.test_doc.path)
        properties = self.doc.get_properties(self.test_doc_path)
        self.assertTrue(properties.locked, msg="Document is not locked")

        self.doc.unlock(self.test_doc.path)
        properties = self.doc.get_properties(self.test_doc_path)
        self.assertFalse(properties.locked, msg="Document is locked")

    def test_get_properties(self):
        """ Get the properites of a document and check the attributes """
        d = self.doc.get_properties(self.test_doc.path)
        contains_keys = self.document_object(d)
        self.assertTrue(contains_keys) # make sure it contains the expected attributes

    def tearDown(self):
        self.doc.delete(self.test_doc_path)


class PropertyTest(TestCase):
    pass


class PropertyGroupTest(TestCase):

    def setUp(self):
        self.test_document = create_test_document_on_openkm()
        self.property_group = client.PropertyGroup()
        self.document = client.Document()
        self.new_group = 'okg:customProperties'

    def test_add_and_remove_group(self):
        """
        Creates a new document
        Adds a property group (which must already exist on OpenKM) to a document
        Checks the property group has been added to the document
        Removes the group
        Checks it has been removed
        Deletes document
        """
        self.property_group.add_group(self.test_document.path, self.new_group)
        property_groups = self.property_group.get_groups(self.test_document.path)
        assigned_property_group = property_groups.item[0].name
        self.assertEqual(assigned_property_group, self.new_group, msg="Assigned property group not as expected")
        self.property_group.remove_group(self.test_document.path, self.new_group)
        property_groups = self.property_group.get_groups(self.test_document.path)
        if property_groups:
            raise Exception('Document has property groups %s' % property_groups)

    def test_get_all_groups(self):
        pass

    def test_get_properties(self):
        pass

    def test_set_properties(self):
        pass

    def test_has_group(self):
        pass

    def tearDown(self):
        delete_test_document_on_openkm()

def get_test_document_path():
    return '%snotes.pdf' % settings.OPENKM['configuration']['UploadRoot']

def create_test_document_on_openkm():
    document = client.Document()
    test_doc = document.new()
    test_doc.path = get_test_document_path()
    document.create(test_doc, "hf7438hf7843h378ot4837ht7")
    return document.get_properties(test_doc.path)

def delete_test_document_on_openkm():
    d = client.Document()
    d.delete(get_test_document_path())


class NoteTest(TestCase):

    def setUp(self):
        self.document = client.Document()
        self.note = client.Note()
        self.test_document = create_test_document_on_openkm()

    def test_add_and_remove(self):
        # add a note
        text = 'hello, this is a note'
        meta = self.note.add(self.test_document.path, text)

        # remove it
        self.note.remove(meta.path)

    def test_get_list(self):
        """
        Add some notes to a document and retrieve them
        """
        # add three notes
        notes = ('one', 'two', 'three')
        for note in notes:
            self.note.add(self.test_document.path, note)

        # test that the notes returned match those added
        list = self.note.list(self.test_document.path)
        for entered, note in zip(notes, list.item):
            self.assertEqual(entered, note.text)
            self.note.remove(note.path)

    def test_get(self):
        text = 'Knock, knock...'
        note = self.note.add(self.test_document.path, text)
        note_meta = self.note.get(note.path)
        self.assertEqual(note_meta.text, text, msg='Returned note does not match')
        self.note.remove(note_meta.path)

    def tearDown(self):
        delete_test_document_on_openkm()


class KeywordTest(TestCase):

    KEYWORDS = ('One', 'Two', 'Three', 'Hammertime!')

    def setUp(self):
        self.keyword = facades.Keyword()
        self.test_document = create_test_document_on_openkm()

    def test_add(self):
        for keyword in self.KEYWORDS:
            self.keyword.add(self.test_document.path, keyword)

    def test_remove(self):
        for keyword in self.KEYWORDS:
            self.keyword.remove(self.test_document.path, keyword)

    def tearDown(self):
        delete_test_document_on_openkm()


class SyncKeywordsTest(TestCase):

    def setUp(self):
        self.document = models.OpenKmDocument()
        self.document.tag_set = u'One, Two, Three'
        self.sync_keywords = sync.SyncKeywords()
        self.test_document = create_test_document_on_openkm()
        self.path = self.test_document.path
        self.tags = self.sync_keywords.get_tags_from_document(self.document)

    def test_get_tags_from_resource(self):
        """
        Should take a a comma separated string of tags and return a list
        """
        self.assertTrue(isinstance(self.tags, list), msg="Tags should be returned as a list")

    def test_tags_are_unicode(self):
        tags = self.sync_keywords.get_tags_from_document(self.document)
        for tag in tags:
            self.assertTrue(isinstance(tag, unicode), msg="%s is not a string, it is %s" % (tag, type(tag)))

    def test_add_keyword_to_openkm_document(self):
        self.sync_keywords.add_keyword_to_openkm_document(self.path, 'Example')

        # cleanup
        self.sync_keywords.keyword.remove(self.path, 'Example')

    def test_write_keywords_to_openkm_document(self):
        self.sync_keywords.write_keywords_to_openkm_document(self.path, self.tags)

    def tearDown(self):
        delete_test_document_on_openkm()


class CategoryTest(TestCase):

    def setUp(self):
        self.category = facades.Category()
        self.repository = client.Repository()

    def test_get_category_root_object_structure(self):
        category_root = self.category.get_category_root()
        attrs = ('author', 'created', 'hasChilds', 'path', 'permissions', 'subscribed', 'uuid')
        for attr in attrs:
            self.assertTrue(hasattr(category_root, attr), msg="%s is not an attribute of the object returned \
            by category root" % attr)

    def test_category_root_path(self):
        category_root = self.category.get_category_root()
        expected = "/okm:categories"
        self.assertEquals(category_root.path, expected, msg="Category root returned %s was not %s" \
        % (category_root.path, expected))

    def test_create_and_remove(self):
        """
        Test these together so we clean up after ourselves
        """
        base_path = self.category.get_category_root().path
        new_category_name = 'UnitTest'
        new_category_path = self.category.construct_valid_path_string(base_path, new_category_name)

        # create the category
        expected_path = new_category_path
        new_category = self.category.create(new_category_path)
        self.assertEquals(new_category.path, expected_path)

        # remove the path
        self.category.remove(new_category.path)

        # test that the category has been removed
        self.assertFalse(self.repository.has_node(new_category.path), msg="Category has not been removed \
        node %s found" % new_category.path)

    def test_construct_valid_path_string(self):
        base_path = '/okm:categories'
        category = 'Products'
        expected = '/okm:categories/Products'
        returned = self.category.construct_valid_path_string(base_path, category)
        self.assertEquals(expected, returned, msg="Returned path %s did not match the expected path %s" %\
                                                  (returned, expected))


class MockResource(object):
    """
    Creates a mock resource, with populated many-to-many fields to be used in tests
    """
    def __init__(self):
        self.sync_categories = sync.SyncCategories()

    def generate_test_resource(self):
        """
        Creates a Resource to be used in testing and populates the many-to-many fields
        with query sets.  Currently simple calling .all() on the related models
        """
        document = models.TestOpenKmDocument()
        document.save()

        # for each model
        for klass in self.sync_categories.MODEL_CATEGORY_MAP.keys():

            # get the model_set many-to-many function of the Resource object
            method_name = '%s' % klass.__name__.lower()
            _set = getattr(document, method_name)

            # populate the resource with objects from the related model
            objects = klass.objects.all()
            for object in objects:
                _set.add(object)

        return document

    def populate_test_model(self, model_klass, related_model_klasses):
        """
        Populates a model to be used in testing and populates the many-to-many fields
        with query sets.  Currently simple calling .all() on the related models.
        Assumes that the naming convention for related model function names if
        [model_name_lowercase]_set (this comes from a legacy project)
        :param model_klass: the main model class
        :param related_model_klasses: an iterable of related model classes
        """
        main_model = model_klass()
        main_model.save()

        # for each model
        for klass in related_model_klasses:

            # get the many-to-many function of the model_klass object
            method_name = '%s' % klass.__name__.lower()
            _set = getattr(main_model, method_name)

            # populate the model_klass instance with objects from the related model
            objects = klass.objects.all()
            for object in objects:
                _set.add(object)

        return main_model


class DirectoryListingTest(TestCase):

    def setUp(self):
        self.dir = facades.DirectoryListing()

    def test_traverse(self):
        self.dir.traverse_folders('/okm:categories/')


class SyncFolderListTest(TestCase):

    def setUp(self):
        self.folder_list = sync.SyncFolderList()

    def test_get_list_of_root_paths(self):
        paths = self.folder_list.get_list_of_root_paths()
        self.assertTrue(isinstance(paths, list), msg="Expected return value to be a list")


class FileSystemTest(TestCase):

    def setUp(self):
        self.file_system = facades.FileSystem()
        self.django_str = 'Regions / Areas'
        self.openkm_str = 'Regions -- Areas'

    def test_normalise_django_path(self):
        openkm_normalised = self.file_system.normalise_string_for_openkm(self.django_str)
        self.assertEqual(openkm_normalised, self.openkm_str, msg="%s not as expected %s" % (openkm_normalised, self.openkm_str))

    def test_denormalise_openkm_path(self):
        denormalised = self.file_system.denormalise_openkm_string(self.openkm_str)
        self.assertEqual(denormalised, self.django_str, msg="%s not as expected %s" % (denormalised, self.openkm_str))


class TaxonomyTest(TestCase):

    def setUp(self):
        self.taxonomy = facades.Taxonomy()
        self.folders = ['EMEA', '2012', 'Team']

    def test_generate_path(self):
        self.taxonomy.generate_path(self.folders)

    def test_generate_path_dependencies(self):
        self.taxonomy.generate_path_dependencies(self.folders)

    def test_build_path(self):
        dependencies = self.taxonomy.generate_path_dependencies(self.folders)
        self.taxonomy.build_path(dependencies)


def get_content_for_upload():
    """
    Generates a file like object with random data and returns it in a form ready to be passed
    over the wire via SOAP
    """
    return utils.make_file_java_byte_array_compatible(open('manage.py', 'r'))


class CustomWebServicesTest(TestCase):
    """
    Test the custom web services added for efficiency.  Note that these are not available
    in standard OpenKM
    """
    def setUp(self):
        # get a file for testing
        self.document = client.Document()
        self.content = get_content_for_upload()
        self.data = self._get_data()

    def test_create_document_data_object(self):
        """
        Should return a new instance of documentData (a custom class which contains
        an instance of Document and also multiple PropertyGroups with Properties
        """
        data = self.document.create_document_data_object()
        msg = "%s was not expected %s" % (data.__class__.__name__, 'documentData')
        self.assertEquals(data.__class__.__name__, 'documentData', msg)

    def test_create_group_properties_object(self):
        """
        Should return a new instance of GroupProperties
        """
        data = self.document.create_group_properties_object()
        msg = "%s was not expected %s" % (data.__class__.__name__, 'groupProperties')
        self.assertEquals(data.__class__.__name__, 'groupProperties', msg)

    def test_create_category_folder_object(self):
        """
        Should return an instance of Folder
        """
        path = "/okm:categories/Industries/Chemicals"
        data = self.document.create_category_folder_object(path)
        msg = "%s was not expected %s" % (data.__class__.__name__, 'folder')
        self.assertEquals(data.__class__.__name__, 'folder', msg)

    def _get_data(self):
        """
        Returns a populated data instance to be passed as a param to Document.create_document()
        """
        data = self.document.create_document_data_object()
        data.document.path = '%s%s' % (settings.OPENKM['configuration']['UploadRoot'], '123.pdf')

        # add keywords
        data.document.keywords += ['one', 'two', 'three']

        # add categories
        path = "/okm:categories/Industries/Chemicals"
        category = self.document.create_category_folder_object(path)
        data.document.categories.append(category)

        # initialise list nodes
        data.document.notes = []
        data.document.subscriptors = []

        # add properties
        sync_properties = sync.SyncProperties()
        properties = self._get_properties_dict()
        data.properties = sync_properties.populate_property_group(properties)

        return data



    def _get_properties_dict(self):
        model = models.OpenKmDocument()
        today = model.okm_date_string(datetime.date.today())
        one_year_from_now = model.okm_date_string(datetime.date.today() + datetime.timedelta(365))
        return {
            'okg:customProperties': {
                'okp:customProperties.title': 'One Flew Over...',
                'okp:customProperties.description': 'One Flew Over a description',
                'okp:customProperties.languages': 'en',
                },
            'okg:salesProperties': {
                'okp:salesProperties.assetType': 'solutionMaps',
                },
            'okg:gsaProperties': {
                'okp:gsaProperties.gsaPublishedStatus': 'Published', # Published || Not Published || Awaiting moderation
                'okp:gsaProperties.startDate': today,
                'okp:gsaProperties.expirationDate': one_year_from_now,
                }
        }

    def test_create_document(self):
        try:
            document = client.Document()
            okm_document = document.create_document(self.content, self.data)
        except suds.WebFault, e:
            print 'Caught suds.WebFault.  Document already exists on server: ', e.message

    def test_update_document(self):
        document = client.Document()
        document.update_document(self.data)
