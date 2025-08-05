import pytest
from app.shared.schemas import PaginatedResponse, PaginationMeta, create_pagination_meta


class TestPaginatedResponse:
    def test_paginated_response_creation(self):
        # Test basic creation
        data = [1, 2, 3]
        meta = PaginationMeta(total=3, page=1, per_page=10, pages=1, has_next=False, has_prev=False)
        
        response = PaginatedResponse(data=data, meta=meta)
        
        assert response.data == data
        assert response.meta == meta

    def test_paginated_response_empty_data(self):
        # Test with empty data
        data = []
        meta = PaginationMeta(total=0, page=1, per_page=10, pages=0, has_next=False, has_prev=False)
        
        response = PaginatedResponse(data=data, meta=meta)
        
        assert response.data == []
        assert response.meta.total == 0

    def test_paginated_response_generic_typing(self):
        # Test with different data types
        string_data = ["a", "b", "c"]
        meta = PaginationMeta(total=3, page=1, per_page=10, pages=1, has_next=False, has_prev=False)
        
        response = PaginatedResponse[str](data=string_data, meta=meta)
        
        assert response.data == string_data

    def test_paginated_response_dict_data(self):
        # Test with dictionary data
        dict_data = [{"id": 1, "name": "test"}]
        meta = PaginationMeta(total=1, page=1, per_page=10, pages=1, has_next=False, has_prev=False)
        
        response = PaginatedResponse[dict](data=dict_data, meta=meta)
        
        assert response.data == dict_data


class TestCreatePaginationMeta:
    def test_create_pagination_meta_first_page(self):
        # Test first page with results
        meta = create_pagination_meta(skip=0, limit=10, total=25)
        
        assert meta.total == 25
        assert meta.page == 1
        assert meta.per_page == 10
        assert meta.pages == 3  # 25 items / 10 per page = 3 pages

    def test_create_pagination_meta_middle_page(self):
        # Test middle page
        meta = create_pagination_meta(skip=10, limit=10, total=25)
        
        assert meta.total == 25
        assert meta.page == 2  # skip=10, limit=10 means page 2
        assert meta.per_page == 10
        assert meta.pages == 3

    def test_create_pagination_meta_last_page(self):
        # Test last page
        meta = create_pagination_meta(skip=20, limit=10, total=25)
        
        assert meta.total == 25
        assert meta.page == 3  # skip=20, limit=10 means page 3
        assert meta.per_page == 10
        assert meta.pages == 3

    def test_create_pagination_meta_empty_results(self):
        # Test with no results
        meta = create_pagination_meta(skip=0, limit=10, total=0)
        
        assert meta.total == 0
        assert meta.page == 1
        assert meta.per_page == 10
        assert meta.pages == 1  # Updated: empty results show 1 page, not 0

    def test_create_pagination_meta_exact_division(self):
        # Test when total is exactly divisible by limit
        meta = create_pagination_meta(skip=0, limit=10, total=30)
        
        assert meta.total == 30
        assert meta.page == 1
        assert meta.per_page == 10
        assert meta.pages == 3  # 30 / 10 = 3 exactly

    def test_create_pagination_meta_single_result(self):
        # Test with single result
        meta = create_pagination_meta(skip=0, limit=10, total=1)
        
        assert meta.total == 1
        assert meta.page == 1
        assert meta.per_page == 10
        assert meta.pages == 1

    def test_create_pagination_meta_limit_one(self):
        # Test with limit of 1
        meta = create_pagination_meta(skip=0, limit=1, total=5)
        
        assert meta.total == 5
        assert meta.page == 1
        assert meta.per_page == 1
        assert meta.pages == 5

    def test_create_pagination_meta_large_skip(self):
        # Test with large skip value
        meta = create_pagination_meta(skip=100, limit=10, total=25)
        
        assert meta.total == 25
        assert meta.page == 11  # skip=100, limit=10 means page 11
        assert meta.per_page == 10
        assert meta.pages == 3  # Still only 3 pages of actual data

    def test_create_pagination_meta_zero_limit(self):
        # Test with zero limit (edge case that causes division by zero)
        with pytest.raises(ZeroDivisionError):
            create_pagination_meta(skip=0, limit=0, total=10)

    def test_create_pagination_meta_page_calculation(self):
        # Test page calculation edge cases
        test_cases = [
            (0, 10, 1),    # skip=0, limit=10 -> page 1
            (5, 10, 1),    # skip=5, limit=10 -> page 1 (partial first page)
            (10, 10, 2),   # skip=10, limit=10 -> page 2
            (15, 10, 2),   # skip=15, limit=10 -> page 2 (partial second page)
            (20, 10, 3),   # skip=20, limit=10 -> page 3
        ]
        
        for skip, limit, expected_page in test_cases:
            meta = create_pagination_meta(skip=skip, limit=limit, total=100)
            assert meta.page == expected_page, f"skip={skip}, limit={limit} should give page {expected_page}"

    def test_create_pagination_meta_pages_calculation(self):
        # Test pages calculation edge cases  
        test_cases = [
            (0, 10, 1),     # total=0 -> 1 page (empty results still show 1 page)
            (1, 10, 1),     # total=1 -> 1 page
            (10, 10, 1),    # total=10, limit=10 -> 1 page
            (11, 10, 2),    # total=11, limit=10 -> 2 pages
            (20, 10, 2),    # total=20, limit=10 -> 2 pages
            (21, 10, 3),    # total=21, limit=10 -> 3 pages
        ]
        
        for total, limit, expected_pages in test_cases:
            meta = create_pagination_meta(skip=0, limit=limit, total=total)
            assert meta.pages == expected_pages, f"total={total}, limit={limit} should give {expected_pages} pages"

    def test_create_pagination_meta_return_type(self):
        # Test return type is PaginationMeta model
        meta = create_pagination_meta(skip=0, limit=10, total=25)
        
        assert isinstance(meta, PaginationMeta)
        assert hasattr(meta, 'total')
        assert hasattr(meta, 'page')
        assert hasattr(meta, 'per_page')
        assert hasattr(meta, 'pages')

    def test_create_pagination_meta_values_are_integers(self):
        # Test all values are integers
        meta = create_pagination_meta(skip=0, limit=10, total=25)
        
        assert isinstance(meta.total, int)
        assert isinstance(meta.page, int)
        assert isinstance(meta.per_page, int)
        assert isinstance(meta.pages, int)