"""
Module for filtering papers based on company affiliations.
"""

from typing import List, Dict, Any, Set, Tuple
import re
import logging


class CompanyAffiliationFilter:
    """Class to filter papers based on company affiliations."""

    # Keywords that typically indicate academic institutions
    ACADEMIC_KEYWORDS = {
        "university", "college", "institute", "school", "academy", "laboratory", 
        "hospital", "clinic", "medical center", "research center", "dept", 
        "department", "faculty"
    }
    
    # Keywords that typically indicate pharmaceutical/biotech companies
    PHARMA_KEYWORDS = {
        "pharmaceutical", "pharma", "biotech", "biotechnology", "therapeutics",
        "inc", "ltd", "llc", "corp", "corporation", "gmbh", "co", "company",
        "bioscience", "biopharm", "biopharma", "genomics", "genetics"
    }
    
    # Known pharmaceutical/biotech companies (common ones)
    KNOWN_COMPANIES = {
        "pfizer", "merck", "novartis", "roche", "johnson & johnson", "janssen",
        "astrazeneca", "gsk", "glaxosmithkline", "bristol-myers squibb", "bms",
        "sanofi", "abbvie", "eli lilly", "amgen", "gilead", "biogen",
        "celgene", "regeneron", "vertex", "alexion", "alnylam", "moderna",
        "biontech", "curevac", "genentech", "novo nordisk", "takeda",
        "bayer", "boehringer ingelheim", "astellas", "daiichi sankyo",
        "otsuka", "teva", "mylan", "viatris", "fresenius", "hikma"
    }
    
    def __init__(self, debug: bool = False):
        """
        Initialize the filter.
        
        Args:
            debug: Enable debug logging
        """
        self.logger = logging.getLogger(__name__)
        if debug:
            logging.basicConfig(level=logging.DEBUG)
    
    def filter_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter papers to include only those with at least one author from a 
        pharmaceutical/biotech company.
        
        Args:
            papers: List of paper details
            
        Returns:
            List of filtered papers with added company information
        """
        filtered_papers = []
        
        for paper in papers:
            non_academic_authors = []
            company_affiliations = []
            
            # Process each author's affiliation
            for i, affiliation in enumerate(paper.get("Affiliations", [])):
                is_academic, companies = self._analyze_affiliation(affiliation)
                
                if not is_academic and companies:
                    # This author is affiliated with a company
                    if i < len(paper.get("Authors", [])):
                        author_name = paper["Authors"][i]
                        non_academic_authors.append(author_name)
                    
                    company_affiliations.extend(companies)
            
            # Only include papers with at least one company-affiliated author
            if non_academic_authors:
                # Add the new fields to the paper
                paper["Non-academic Author(s)"] = non_academic_authors
                paper["Company Affiliation(s)"] = list(set(company_affiliations))  # Remove duplicates
                
                # Get corresponding author email (first one if multiple)
                corresponding_emails = paper.get("Corresponding Author Emails", [])
                paper["Corresponding Author Email"] = corresponding_emails[0] if corresponding_emails else ""
                
                filtered_papers.append(paper)
                self.logger.debug(f"Added paper: {paper['Title']}")
        
        return filtered_papers
    
    def _analyze_affiliation(self, affiliation: str) -> Tuple[bool, List[str]]:
        """
        Analyze an affiliation string to determine if it's academic or company.
        
        Args:
            affiliation: Affiliation string
            
        Returns:
            Tuple of (is_academic, list_of_companies)
        """
        if not affiliation:
            return True, []
        
        # Convert to lowercase for case-insensitive matching
        aff_lower = affiliation.lower()
        
        # Check for academic keywords
        has_academic_keyword = any(keyword in aff_lower for keyword in self.ACADEMIC_KEYWORDS)
        
        # Check for known companies
        found_companies = []
        for company in self.KNOWN_COMPANIES:
            if company in aff_lower:
                found_companies.append(company)
        
        # Check for pharma/biotech keywords
        has_pharma_keyword = any(keyword in aff_lower for keyword in self.PHARMA_KEYWORDS)
        
        # If it has academic keywords but no company indicators, consider it academic
        if has_academic_keyword and not found_companies and not has_pharma_keyword:
            return True, []
        
        # If it has company indicators, consider it non-academic
        if found_companies or has_pharma_keyword:
            # Try to extract company names from the affiliation
            if not found_companies:
                found_companies = self._extract_company_names(affiliation)
            return False, found_companies
        
        # Default to academic if unclear
        return True, []
    
    def _extract_company_names(self, affiliation: str) -> List[str]:
        """
        Attempt to extract company names from an affiliation string.
        
        Args:
            affiliation: Affiliation string
            
        Returns:
            List of potential company names
        """
        # Simple extraction based on common patterns
        companies = []
        
        # Split by common delimiters
        parts = re.split(r'[,;]', affiliation)
        
        for part in parts:
            part = part.strip()
            
            # Skip if it contains academic indicators
            if any(keyword in part.lower() for keyword in self.ACADEMIC_KEYWORDS):
                continue
                
            # Check if it contains pharma/biotech keywords
            if any(keyword in part.lower() for keyword in self.PHARMA_KEYWORDS):
                companies.append(part)
        
        return companies