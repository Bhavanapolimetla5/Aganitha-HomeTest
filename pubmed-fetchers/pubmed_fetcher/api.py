
from typing import List, Dict, Any, Optional
import requests
from xml.etree import ElementTree
import logging


class PubMedAPI:
    """Class to interact with the PubMed API."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    def __init__(self, api_key: Optional[str] = None, debug: bool = False):
        """
        Initialize the PubMed API client.
        
        Args:
            api_key: Optional API key for higher rate limits
            debug: Enable debug logging
        """
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        
    def search(self, query: str, max_results: int = 100) -> List[str]:
        """
        Search for papers matching the query and return their PubMed IDs.
        
        Args:
            query: PubMed query string
            max_results: Maximum number of results to return
            
        Returns:
            List of PubMed IDs
        """
        search_url = f"{self.BASE_URL}esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": max_results,
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
            
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])
        
        self.logger.debug(f"Found {len(pmids)} papers for query: {query}")
        return pmids
    
    def fetch_details(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch detailed information for a list of PubMed IDs.
        
        Args:
            pmids: List of PubMed IDs
            
        Returns:
            List of paper details
        """
        if not pmids:
            return []
            
        fetch_url = f"{self.BASE_URL}efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
            
        response = requests.get(fetch_url, params=params)
        response.raise_for_status()
        
        return self._parse_xml_response(response.text)
    
    def _parse_xml_response(self, xml_text: str) -> List[Dict[str, Any]]:
        """
        Parse the XML response from PubMed.
        
        Args:
            xml_text: XML response text
            
        Returns:
            List of parsed paper details
        """
        root = ElementTree.fromstring(xml_text)
        papers = []
        
        for article in root.findall(".//PubmedArticle"):
            paper = {}
            
            # Extract PubMed ID
            pmid_elem = article.find(".//PMID")
            paper["PubmedID"] = pmid_elem.text if pmid_elem is not None else ""
            
            # Extract title
            title_elem = article.find(".//ArticleTitle")
            paper["Title"] = title_elem.text if title_elem is not None else ""
            
            # Extract publication date
            pub_date_elem = article.find(".//PubDate")
            if pub_date_elem is not None:
                year = pub_date_elem.findtext("Year") or ""
                month = pub_date_elem.findtext("Month") or ""
                day = pub_date_elem.findtext("Day") or ""
                paper["Publication Date"] = f"{year}-{month}-{day}".strip("-")
            else:
                paper["Publication Date"] = ""
            
            # Extract authors and affiliations
            authors = []
            affiliations = []
            corresponding_emails = []
            
            for author in article.findall(".//Author"):
                last_name = author.findtext("LastName") or ""
                fore_name = author.findtext("ForeName") or ""
                full_name = f"{fore_name} {last_name}".strip()
                
                if full_name:
                    authors.append(full_name)
                
                # Extract affiliation information
                affiliation = author.findtext("AffiliationInfo/Affiliation") or ""
                if affiliation:
                    affiliations.append(affiliation)
                
                # Check if corresponding author and extract email
                if author.get("Corresponding") == "Y":
                    email_elem = author.find(".//AffiliationInfo/Affiliation")
                    if email_elem is not None:
                        email_text = email_elem.text
                        # Simple email extraction
                        if "@" in email_text:
                            # Extract email from text
                            import re
                            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email_text)
                            if email_match:
                                corresponding_emails.append(email_match.group())
            
            paper["Authors"] = authors
            paper["Affiliations"] = affiliations
            paper["Corresponding Author Emails"] = corresponding_emails
            
            papers.append(paper)
        
        return papers