"""
Module for handling CSV output of filtered papers.
"""

from typing import List, Dict, Any, Optional
import csv
import sys
import logging


class CSVOutputHandler:
    """Class to handle CSV output of filtered papers."""

    def __init__(self, debug: bool = False):
        """
        Initialize the output handler.
        
        Args:
            debug: Enable debug logging
        """
        self.logger = logging.getLogger(__name__)
        if debug:
            logging.basicConfig(level=logging.DEBUG)
    
    def write_to_csv(self, papers: List[Dict[str, Any]], filename: Optional[str] = None) -> None:
        """
        Write filtered papers to a CSV file or print to console.
        
        Args:
            papers: List of filtered paper details
            filename: Optional filename to save the CSV. If None, prints to console.
        """
        if not papers:
            self.logger.warning("No papers to write to CSV")
            return
        
        # Define the CSV columns
        fieldnames = [
            "PubmedID",
            "Title",
            "Publication Date",
            "Non-academic Author(s)",
            "Company Affiliation(s)",
            "Corresponding Author Email"
        ]
        
        # Prepare rows for CSV
        rows = []
        for paper in papers:
            row = {
                "PubmedID": paper.get("PubmedID", ""),
                "Title": paper.get("Title", ""),
                "Publication Date": paper.get("Publication Date", ""),
                "Non-academic Author(s)": "; ".join(paper.get("Non-academic Author(s)", [])),
                "Company Affiliation(s)": "; ".join(paper.get("Company Affiliation(s)", [])),
                "Corresponding Author Email": paper.get("Corresponding Author Email", "")
            }
            rows.append(row)
        
        # Write to file or print to console
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            self.logger.info(f"Results written to {filename}")
        else:
            # Print to console
            writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)