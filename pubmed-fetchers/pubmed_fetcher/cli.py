"""
Command-line interface for the PubMed paper fetcher.
"""

import argparse
import sys
from typing import Optional

from .api import PubMedAPI
from .filter import CompanyAffiliationFilter
from .output import CSVOutputHandler


def main() -> None:
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Fetch research papers from PubMed with authors from pharmaceutical/biotech companies"
    )
    
    parser.add_argument(
        "query",
        help="PubMed query string (supports full query syntax)"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="Filename to save the results. If not provided, prints to console."
    )
    
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Print debug information during execution"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        default=100,
        help="Maximum number of results to fetch (default: 100)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize components
        api = PubMedAPI(debug=args.debug)
        filter = CompanyAffiliationFilter(debug=args.debug)
        output_handler = CSVOutputHandler(debug=args.debug)
        
        # Step 1: Search for papers
        print(f"Searching PubMed for: {args.query}")
        pmids = api.search(args.query, max_results=args.max_results)
        
        if not pmids:
            print("No papers found matching the query.")
            return
        
        print(f"Found {len(pmids)} papers. Fetching details...")
        
        # Step 2: Fetch paper details
        papers = api.fetch_details(pmids)
        
        if not papers:
            print("Failed to fetch paper details.")
            return
        
        # Step 3: Filter papers with company affiliations
        print("Filtering papers with pharmaceutical/biotech company affiliations...")
        filtered_papers = filter.filter_papers(papers)
        
        if not filtered_papers:
            print("No papers with pharmaceutical/biotech company affiliations found.")
            return
        
        print(f"Found {len(filtered_papers)} papers with company affiliations.")
        
        # Step 4: Output results
        output_handler.write_to_csv(filtered_papers, args.file)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()