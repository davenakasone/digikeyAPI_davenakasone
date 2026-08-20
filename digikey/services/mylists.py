"""
MyLists and BOM Management service for DigiKey SDK.
"""
from typing import Any, Dict, List, Optional
from digikey.core.base_client import BaseClient


class MyListsService:
    """
    Service wrapper for DigiKey MyLists (BOMs and Saved Lists) API.
    """

    def __init__(self, client: BaseClient):
        self._client = client

    def get_lists(self) -> List[Dict[str, Any]]:
        """Retrieves all saved lists / BOMs for the authorized account."""
        url = "/mylists/v1/lists"
        resp = self._client.get(url)
        return resp.get("Lists", resp if isinstance(resp, list) else [])

    def get_list_details(self, list_id: str) -> Dict[str, Any]:
        """Retrieves items in a specific list / BOM."""
        url = f"/mylists/v1/lists/{list_id}"
        return self._client.get(url)

    def create_list(self, name: str, parts: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Creates a new BOM list."""
        url = "/mylists/v1/lists"
        payload = {"ListName": name, "Parts": parts or []}
        return self._client.post(url, json_data=payload)
