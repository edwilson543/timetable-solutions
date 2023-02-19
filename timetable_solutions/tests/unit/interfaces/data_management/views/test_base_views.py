from interfaces.data_management.views import base_views


class TestSearchViewProperties:
    """Tests for the properties defined on the SearchView class."""

    class FakeSearchView(base_views.SearchView):
        displayed_fields = {
            "test_field_one": "Test Field One",
            "test_field_two": "Test Field Two",
        }

    def test_display_field_names_shown_in_correct_order(self):
        field_names = self.FakeSearchView().display_field_names

        assert field_names == ["test_field_one", "test_field_two"]

    def test_human_field_names_shown_in_correct_order(self):
        field_names = self.FakeSearchView().human_field_names

        assert field_names == ["Test Field One", "Test Field Two"]
