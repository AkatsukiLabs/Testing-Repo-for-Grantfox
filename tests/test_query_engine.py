"""Unit tests for query engine operators, pagination, and sorting."""

import unittest

from spacex import SpaceX, ValidationError


class TestQueryEngine(unittest.TestCase):
    """Test suite for query evaluation, pagination mathematics, and filtering operators."""

    def setUp(self) -> None:
        """Initialize client before test execution."""
        self.client = SpaceX()

    def test_pagination_limits_and_pages(self) -> None:
        """Verify page count and bounds calculation across collections."""
        result = self.client.launches.query(
            options={"limit": 2, "page": 1}
        )
        self.assertEqual(len(result.docs), 2)
        self.assertEqual(result.page, 1)
        self.assertTrue(result.has_next_page)
        self.assertFalse(result.has_prev_page)
        self.assertEqual(result.next_page, 2)
        self.assertIsNone(result.prev_page)

    def test_pagination_second_page(self) -> None:
        """Verify second page pagination cursor state."""
        result = self.client.launches.query(
            options={"limit": 2, "page": 2}
        )
        self.assertEqual(len(result.docs), 2)
        self.assertEqual(result.page, 2)
        self.assertTrue(result.has_prev_page)
        self.assertEqual(result.prev_page, 1)

    def test_range_operators(self) -> None:
        """Verify $gt and $lte operators on numeric fields."""
        result = self.client.launches.query(
            query={"flight_number": {"$gt": 50, "$lte": 150}}
        )
        self.assertGreater(result.total_docs, 0)
        for doc in result.docs:
            self.assertGreater(doc.flight_number, 50)
            self.assertLessEqual(doc.flight_number, 150)

    def test_in_operator(self) -> None:
        """Verify $in operator matching against allowed set."""
        result = self.client.rockets.query(
            query={"name": {"$in": ["Falcon 9", "Starship"]}}
        )
        self.assertEqual(result.total_docs, 2)
        names = {r.name for r in result.docs}
        self.assertEqual(names, {"Falcon 9", "Starship"})

    def test_nin_operator(self) -> None:
        """Verify $nin operator excluding specific items."""
        result = self.client.rockets.query(
            query={"name": {"$nin": ["Falcon 1", "Falcon 9"]}}
        )
        self.assertEqual(result.total_docs, 2)
        names = {r.name for r in result.docs}
        self.assertEqual(names, {"Falcon Heavy", "Starship"})

    def test_sorting_ascending_and_descending(self) -> None:
        """Verify sort ordering on flight numbers."""
        asc_res = self.client.launches.query(
            options={"sort": {"flight_number": "asc"}, "limit": 100}
        )
        asc_flights = [d.flight_number for d in asc_res.docs]
        self.assertEqual(asc_flights, sorted(asc_flights))

        desc_res = self.client.launches.query(
            options={"sort": {"flight_number": "desc"}, "limit": 100}
        )
        desc_flights = [d.flight_number for d in desc_res.docs]
        self.assertEqual(desc_flights, sorted(desc_flights, reverse=True))

    def test_nested_path_filtering(self) -> None:
        """Verify dot-notation path evaluation on nested dictionaries."""
        result = self.client.rockets.query(
            query={"engines.type": "raptor"}
        )
        self.assertEqual(result.total_docs, 1)
        self.assertEqual(result.docs[0].name, "Starship")

    def test_regex_filtering(self) -> None:
        """Verify regular expression pattern matching."""
        result = self.client.launches.query(
            query={"name": {"$regex": "^Falcon"}}
        )
        self.assertGreaterEqual(result.total_docs, 2)
        for doc in result.docs:
            self.assertTrue(doc.name.startswith("Falcon"))

    def test_unsupported_operator_raises_validation_error(self) -> None:
        """Verify ValidationError when unknown operator is supplied."""
        with self.assertRaises(ValidationError):
            self.client.launches.query(
                query={"flight_number": {"$unknown_op": 10}}
            )


if __name__ == "__main__":
    unittest.main()
