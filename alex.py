#!/usr/bin/env python3
"""
Standalone Merchant Research Tool

This script researches comprehensive merchant information for e-commerce return processing.
It can take either a merchant name or website URL as input and will automatically:

1. Search the web for the merchant's official information
2. Browse their website and support pages
3. Extract return policies, contact details, and return portal URLs
4. Determine if returns are handled via email or web forms
5. Provide structured merchant data for integration

The script is completely standalone and includes all necessary functionality inline.
No database connection or external dependencies beyond Python packages are required.

Requirements:
- OPENAI_API_KEY environment variable must be set
- Python packages: langchain-openai, beautifulsoup4, requests, playwright, python-dotenv

Usage Examples:
    python standalone_merchant_research.py "Amazon"
    python standalone_merchant_research.py "Best Buy"
    python standalone_merchant_research.py "https://www.target.com"
    python standalone_merchant_research.py "walmart.com"

Output:
    Returns a Python dictionary with merchant information including:
    - website: Official website URL
    - return_policy: Detailed return policy summary
    - support_email: Customer support email
    - support_url: Customer support page URL
    - return_policy_url: Return policy information page
    - return_portal_url: Functional return submission portal
    - is_via_email: Boolean indicating if returns require email (vs web form)
    - research_notes: Detailed research process notes
"""

import os
import sys
import json
import argparse
import asyncio
import requests
import re
from typing import Dict, Any, List
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import urllib.parse

from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set USER_AGENT to avoid warnings
if not os.getenv("USER_AGENT"):
    os.environ["USER_AGENT"] = "Mozilla/5.0 (compatible; LangChain MerchantResearcher/1.0)"


def search_web(query: str, context: str = "general") -> str:
    """
    Search the web using OpenAI's built-in web search functionality.

    Args:
        query: The search query
        context: Context for the search ("merchant", "order", "general")

    Returns:
        String with search results
    """
    try:
        # Create LLM instance
        llm = ChatOpenAI(model="gpt-4o", temperature=0)

        # Customize search based on context
        if context == "merchant":
            search_prompt = f"""
            Search for merchant information about: {query}

            Focus on finding:
            - Official website and contact information
            - Return policies and procedures
            - Customer service details
            - Return portal URLs and support pages
            - Business information and legitimacy

            Provide accurate, up-to-date information about this merchant.
            """
        elif context == "order":
            search_prompt = f"""
            Search for order-related information about: {query}

            Focus on:
            - Merchant policies and procedures
            - Return and refund processes
            - Customer service best practices
            - Shipping and delivery information
            - Product information and support

            Keep the response practical and actionable for customer service.
            """
        else:
            search_prompt = f"Search for current information about: {query}"

        try:
            # Try different web search tool configurations
            # First try with web_search_preview
            tool = {"type": "web_search_preview"}
            llm_with_tools = llm.bind_tools([tool])
            response = llm_with_tools.invoke(search_prompt)
            return response.content
        except Exception as preview_error:
            # If web_search_preview fails, try with web_search
            try:
                tool = {"type": "web_search"}
                llm_with_tools = llm.bind_tools([tool])
                response = llm_with_tools.invoke(search_prompt)
                return response.content
            except Exception as search_error:
                # Fallback to direct LLM response
                response = llm.invoke(search_prompt)
                return f"Information about '{query}' (from knowledge base):\n\n{response.content}"

    except Exception as e:
        # Fallback approach - suggest likely URLs for merchants
        if "merchant" in context.lower() or any(
                word in query.lower() for word in ["website", "return", "policy", "contact"]):
            merchant_name = query.lower().replace(' official website', '').replace(' website', '').replace(' ', '')
            fallback_results = [
                f"Web search failed ({str(e)}), suggesting likely URLs for: {query}",
                f"Try browsing: https://www.{merchant_name}.com",
                f"Try browsing: https://{merchant_name}.com",
                f"Try browsing: https://www.{merchant_name}.net",
                "Use browse_webpage tool to check these URLs."
            ]
            return "\n".join(fallback_results)
        else:
            return f"I apologize, but I encountered an error while searching for information about '{query}'. However, I can still help you with general guidance based on my knowledge. Error details: {str(e)}"


def browse_webpage(url: str, purpose: str = "general") -> str:
    """
    Browse webpage using Playwright for better JavaScript support and content extraction.
    Falls back to requests + BeautifulSoup if Playwright fails.

    Args:
        url: The URL to browse and extract content from
        purpose: Purpose of browsing ("merchant_research", "order_support", "general")

    Returns:
        String with the webpage content and relevant links
    """
    try:
        return _browse_with_playwright(url, purpose)
    except Exception as e:
        print(f"Playwright failed ({e}), using requests fallback...")
        return _browse_with_requests(url, purpose)


def _browse_with_playwright(url: str, purpose: str = "general") -> str:
    """
    Use Playwright to browse webpage with better JavaScript support and content extraction.

    Args:
        url: The URL to browse
        purpose: Purpose of browsing for content prioritization

    Returns:
        String with webpage content and relevant links
    """
    try:
        from playwright.async_api import async_playwright

        async def _async_browse():
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    chromium_sandbox=False,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                    ],
                )

                try:
                    page = await browser.new_page()

                    await page.set_viewport_size({"width": 1280, "height": 720})
                    await page.set_extra_http_headers({
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    })

                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(2000)

                    content = await page.content()

                    soup = BeautifulSoup(content, 'html.parser')

                    # Content selectors based on purpose
                    if purpose == "merchant_research":
                        content_selectors = [
                            'main', 'article', '.content', '.policy', '.post-content',
                            '.help-content', '.return-policy', '.support', '.contact',
                            '.customer-service', '.help', '.faq', '.returns', '.refunds',
                            '.exchange', '.warranty', '.customer-care', '.service',
                            '[class*="return"]', '[class*="refund"]', '[class*="exchange"]',
                            '[class*="policy"]', '[class*="support"]', '[class*="help"]',
                            '[id*="return"]', '[id*="refund"]', '[id*="support"]',
                            '[id*="policy"]', '[id*="help"]', '[id*="customer"]'
                        ]
                    else:
                        content_selectors = [
                            'main', 'article', '.content', '.policy', '.post-content',
                            '.help-content'
                        ]

                    # Extract content with prioritization
                    content_text = ""
                    for selector in content_selectors:
                        try:
                            elements = soup.select(selector)
                            for element in elements:
                                content_text += element.get_text(strip=True) + "\n"
                        except Exception:
                            continue

                    # Fallback to body if no content found
                    if not content_text.strip():
                        body = soup.find('body')
                        if body:
                            content_text = body.get_text(strip=True)

                    # Extract relevant links
                    links = _extract_relevant_links(soup, url, purpose)

                    # Format the response
                    response = f"Content from {url} (Playwright):\n\n{content_text[:3000]}"

                    if links:
                        response += "\n\n--- RELEVANT LINKS FOUND ---\n"
                        for link in links:
                            response += f"{link}\n"

                    return response

                finally:
                    await browser.close()

        # Run the async function
        def run_in_new_loop():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(_async_browse())
            finally:
                new_loop.close()

        return run_in_new_loop()

    except Exception as e:
        raise Exception(f"Playwright browsing failed: {str(e)}")


def _browse_with_requests(url: str, purpose: str = "general") -> str:
    """
    Fallback method using requests and BeautifulSoup.

    Args:
        url: The URL to browse
        purpose: Purpose of browsing for content prioritization

    Returns:
        String with webpage content and relevant links
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract main content
        content_text = ""
        for selector in ['main', 'article', '.content', 'body']:
            elements = soup.select(selector)
            for element in elements:
                content_text += element.get_text(strip=True) + "\n"
            if content_text.strip():
                break

        # Extract relevant links
        links = _extract_relevant_links(soup, url, purpose)

        # Format the response
        response_text = f"Content from {url} (Requests):\n\n{content_text[:3000]}"

        if links:
            response_text += "\n\n--- RELEVANT LINKS FOUND ---\n"
            for link in links:
                response_text += f"{link}\n"

        return response_text

    except Exception as e:
        return f"Error browsing {url}: {str(e)}"


def _extract_relevant_links(soup: BeautifulSoup, base_url: str, purpose: str = "general") -> List[str]:
    """
    Extract relevant links from webpage based on purpose.

    Args:
        soup: BeautifulSoup object
        base_url: Base URL for relative links
        purpose: Purpose of browsing for link prioritization

    Returns:
        List of relevant link strings with priorities
    """
    links = []

    # Define keywords based on purpose
    if purpose == "merchant_research":
        high_priority_keywords = [
            'return', 'refund', 'exchange', 'policy', 'help', 'support',
            'contact', 'customer', 'service', 'faq', 'warranty', 'care'
        ]
        medium_priority_keywords = [
            'about', 'terms', 'privacy', 'shipping', 'delivery', 'account',
            'login', 'register', 'order', 'track', 'status'
        ]
    else:
        high_priority_keywords = ['help', 'support', 'contact', 'about']
        medium_priority_keywords = ['policy', 'terms', 'privacy']

    # Extract links
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        text = link.get_text(strip=True).lower()

        if not href:
            continue

        # Make absolute URL
        full_url = urllib.parse.urljoin(base_url, href)

        # Skip javascript, mailto, tel, etc.
        if any(full_url.startswith(prefix) for prefix in ['javascript:', 'mailto:', 'tel:', '#']):
            continue

        # Score the link based on text and URL
        score = 0

        # Check text content
        for keyword in high_priority_keywords:
            if keyword in text:
                score += 100
                break

        if score == 0:
            for keyword in medium_priority_keywords:
                if keyword in text:
                    score += 50
                    break

        # Check URL
        for keyword in high_priority_keywords:
            if keyword in full_url.lower():
                score += 80
                break

        if score == 0:
            for keyword in medium_priority_keywords:
                if keyword in full_url.lower():
                    score += 30
                    break

        # Add link with priority
        if score >= 100:
            priority = "🔴 HIGH"
        elif score >= 50:
            priority = "🟠 MEDIUM"
        elif score >= 20:
            priority = "🟡 LOW"
        else:
            continue  # Skip low-relevance links

        links.append(f"{priority} {text} -> {full_url}")

    # Sort by priority and limit results
    links.sort(key=lambda x: x.count('🔴'), reverse=True)
    return links[:10]  # Return top 10 links


class MerchantResearcher:
    """
    A LangChain-based researcher for finding merchant information.
    """

    def __init__(self):
        """Initialize the researcher with tools."""
        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("❌ Error: OPENAI_API_KEY environment variable is required")

        # Initialize ChatOpenAI
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

        # Create tools
        self.tools = [
            Tool(
                name="web_search",
                description="Search the web for information about merchants, their policies, contact details, and return procedures. Input should be a clear search query.",
                func=lambda query: search_web(query, "merchant"),
            ),
            Tool(
                name="browse_webpage",
                description="Load and read the full content of a specific webpage URL using Playwright for better JavaScript support and merchant research capabilities. Extracts relevant hyperlinks that might lead to return portals. Use this to examine merchant websites, return policy pages, support pages, etc. Input should be a valid URL.",
                func=lambda url: browse_webpage(url, "merchant_research"),
            )
        ]

        # Create agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a specialized AI researcher focused on finding comprehensive merchant information for e-commerce return processing.

Your task is to research merchants and find the following information:
1. Official website URL
2. Return policy (detailed text summary)  
3. Support email address
4. Support URL (general customer service page)
5. Return Policy URL (informational page explaining return policy)
6. Return Portal URL (functional page where customers can submit return/exchange/refund requests)
7. Return process type (is_via_email: true/false)

CRITICAL RESEARCH STRATEGY:
- ALWAYS use web_search first to find the merchant's official website and relevant pages
- ALWAYS follow up search results by using browse_webpage to read the ACTUAL content of relevant pages
- DO NOT rely solely on search result snippets - you MUST browse the actual webpages
- Search for: merchant official website, return policy page, customer service page, support contact
- Browse each relevant URL found in search results to extract detailed information
- Pay special attention to return/refund process instructions

MANDATORY BROWSING STEPS (FOLLOW EXACTLY):
1. Search for merchant official website
2. Browse the main website URL - extract ALL hyperlinks with return/account keywords
3. Browse EVERY promising hyperlink from step 2 (returns, my account, login, support)
4. Search for merchant return policy or returns page
5. Browse return policy pages - extract ALL hyperlinks mentioning returns/refunds/exchanges
6. Browse EVERY hyperlink from step 5 that could be a return portal
7. Search for merchant customer service contact
8. Browse customer service/contact pages - extract return-related hyperlinks
9. Browse ALL return-related hyperlinks found in step 8
10. Search for "merchant name return portal" or "merchant name start return"
11. Browse ANY additional candidate pages found in step 10

RETURN PROCESS ANALYSIS (CRITICAL):
Carefully determine if the merchant handles returns via:
- EMAIL (is_via_email: true): Customer must email support to initiate returns/refunds
- WEB FORM (is_via_email: false): Customer uses online forms/portals to submit return requests

RETURN PORTAL IDENTIFICATION CRITERIA (CRITICAL):
The return portal URL must be the DEDICATED CUSTOMER RETURN PORTAL, not just any submission form.

ABSOLUTELY REJECT these types of pages (DO NOT USE AS RETURN PORTAL):
- Generic login pages (URLs containing /login, /signin, /account/login, /customer/login)
- General account pages without specific return functionality
- Generic "Contact Us" forms
- Customer service submission forms without return specifics
- Help desk or support ticket forms
- General inquiry forms
- FAQ or help pages without submission functionality

PRIORITIZE these types of pages (HIGHEST PRIORITY):
- "Return Center" or "Returns Portal" with visible return forms
- "My Returns" or "Manage Returns" with actual return submission interface
- "Start a Return" or "Begin Return Process" with return forms
- Dedicated return request forms (not general contact forms)
- Pages specifically for returning/exchanging products with visible forms
- Pages with order lookup and return initiation functionality

RESPONSE FORMAT:
Provide your findings in this exact JSON format:
{{
    "website": "https://example.com",
    "return_policy": "Detailed return policy text summary with specific process steps",
    "support_email": "support@example.com",
    "support_url": "https://example.com/support",
    "return_policy_url": "https://example.com/return-policy",
    "return_portal_url": "https://example.com/returns",
    "is_via_email": true,
    "research_notes": "Detailed notes about the research process and how return process type was determined"
}}

IMPORTANT - FINAL VALIDATION:
- Set "is_via_email" to true if returns require email contact, false if online forms are available
- return_policy_url should be the informational page explaining the return policy
- return_portal_url should be the functional page for submitting returns (null if email-based)
- You MUST actually browse and verify that return_portal_url contains submission functionality
- If you cannot find specific information, use null for that field
- Always provide detailed research_notes explaining your findings and why URLs were chosen
- Be thorough and accurate in your research - follow ALL promising hyperlinks"""),
            ("human", "Research merchant: {merchant_name}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        # Create agent
        agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)

        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=12,
            return_intermediate_steps=True,
        )

    def research_merchant(self, merchant_name: str) -> Dict[str, Any]:
        """
        Research a merchant and return structured information.

        Args:
            merchant_name: Name of the merchant to research

        Returns:
            Dictionary with merchant information
        """
        try:
            print(f"\n🔍 Researching merchant: {merchant_name}")
            print("=" * 60)

            # Invoke agent
            result = self.agent_executor.invoke({"merchant_name": merchant_name})

            # Parse the response to extract JSON
            response_text = result['output']

            # Try to extract JSON from the response
            try:
                # Look for JSON in the response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    merchant_info = json.loads(json_match.group())
                else:
                    # Fallback: create structure from text
                    merchant_info = {
                        "website": None,
                        "return_policy": response_text[:1000] if response_text else None,
                        "support_email": None,
                        "support_url": None,
                        "return_policy_url": None,
                        "return_portal_url": None,
                        "is_via_email": None,
                        "research_notes": "Could not parse structured response"
                    }
            except (json.JSONDecodeError, AttributeError):
                # Fallback structure
                merchant_info = {
                    "website": None,
                    "return_policy": response_text[:1000] if response_text else None,
                    "support_email": None,
                    "support_url": None,
                    "return_policy_url": None,
                    "return_portal_url": None,
                    "is_via_email": None,
                    "research_notes": f"Research completed but response parsing failed: {response_text[:200]}..."
                }

            print(f"\n✅ Research completed for {merchant_name}")
            return merchant_info

        except Exception as e:
            print(f"\n❌ Error researching {merchant_name}: {str(e)}")
            return {
                "website": None,
                "return_policy": None,
                "support_email": None,
                "support_url": None,
                "return_policy_url": None,
                "return_portal_url": None,
                "is_via_email": None,
                "research_notes": f"Research failed: {str(e)}"
            }


def extract_merchant_name_from_url(url: str) -> str:
    """
    Extract a merchant name from a website URL.

    Args:
        url: Website URL

    Returns:
        Extracted merchant name
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Remove common prefixes
        if domain.startswith('www.'):
            domain = domain[4:]

        # Split by dots and take the main domain name
        parts = domain.split('.')
        if len(parts) >= 2:
            # Take the second-to-last part as the main name
            main_name = parts[-2]

            # Handle common cases
            if main_name in ['amazon', 'shop', 'store']:
                return main_name.capitalize()

            # Capitalize first letter
            return main_name.capitalize()

        return domain
    except Exception:
        return url


def validate_input(input_str: str) -> tuple[str, str]:
    """
    Validate and determine if input is a merchant name or website.

    Args:
        input_str: Input string (merchant name or website)

    Returns:
        Tuple of (merchant_name, input_type)
    """
    input_str = input_str.strip()

    # Check if it's a URL
    if input_str.startswith(('http://', 'https://', 'www.')):
        return extract_merchant_name_from_url(input_str), 'website'
    elif '.' in input_str and len(input_str.split('.')) >= 2:
        # Looks like a domain without protocol
        return extract_merchant_name_from_url(f"https://{input_str}"), 'domain'
    else:
        # Assume it's a merchant name
        return input_str, 'name'


def research_merchant_standalone(input_str: str) -> Dict[str, Any]:
    """
    Research a merchant by name or website URL.

    Args:
        input_str: Merchant name or website URL

    Returns:
        Dictionary containing merchant information
    """
    print("🔍 Standalone Merchant Research Tool")
    print("=" * 60)
    print("This tool will research comprehensive merchant information including:")
    print("• Official website and contact details")
    print("• Return policies and procedures")
    print("• Customer support information")
    print("• Return portal URLs and process type")
    print("=" * 60)

    # Validate input
    merchant_name, input_type = validate_input(input_str)

    print(f"📋 Input: {input_str}")
    print(f"📊 Input Type: {input_type}")
    print(f"🏪 Merchant Name: {merchant_name}")

    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("\n" + "❌" * 50)
        print("ERROR: OPENAI_API_KEY environment variable is required")
        print("❌" * 50)
        print("\nTo fix this:")
        print("1. Get an OpenAI API key from: https://platform.openai.com/api-keys")
        print("2. Set it as an environment variable:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("3. Or add it to a .env file in the project root:")
        print("   OPENAI_API_KEY=your-api-key-here")
        print("4. Then run the script again")
        return {"error": "OPENAI_API_KEY not found"}

    try:
        # Initialize researcher
        print("\n🤖 Initializing AI researcher...")
        print("   • Loading LangChain tools...")
        print("   • Setting up web search and browsing capabilities...")
        researcher = MerchantResearcher()

        # Research the merchant
        print(f"\n🔍 Researching {merchant_name}...")
        print("   • This may take 1-3 minutes depending on merchant complexity")
        print("   • The AI will search the web and browse multiple pages")
        print("   • Progress will be shown below...")
        merchant_info = researcher.research_merchant(merchant_name)

        # Display results like the original merchant_research.py
        print("\n" + "=" * 50)
        print("📋 KEY FINDINGS:")
        print("=" * 50)
        print(f"Website: {merchant_info.get('website', 'Not found')}")
        print(f"Support Email: {merchant_info.get('support_email', 'Not found')}")
        print(f"Return Policy URL: {merchant_info.get('return_policy_url', 'Not found')}")
        print(f"Return Portal URL: {merchant_info.get('return_portal_url', 'Not found')}")
        is_via_email = merchant_info.get('is_via_email')
        if is_via_email is not None:
            return_type = "Email-based" if is_via_email else "Web form-based"
            print(f"Return Process: {return_type} (is_via_email: {is_via_email})")
        else:
            print("Return Process: Could not determine")
        print(f"Research Notes: {merchant_info.get('research_notes', 'None')[:150]}...")

        return merchant_info

    except Exception as e:
        print(f"\n❌ Error during research: {str(e)}")
        print("\nTroubleshooting tips:")
        print("• Check your internet connection")
        print("• Verify your OpenAI API key is valid and has credits")
        print("• Try a different merchant name or URL")
        print("• Some websites may block automated access")
        return {
            "website": None,
            "return_policy": None,
            "support_email": None,
            "support_url": None,
            "return_policy_url": None,
            "return_portal_url": None,
            "is_via_email": None,
            "research_notes": f"Research failed: {str(e)}"
        }


def print_usage_help():
    """Print detailed usage help and examples."""
    print("""
🔍 STANDALONE MERCHANT RESEARCH TOOL
=====================================

This tool researches comprehensive merchant information for e-commerce return processing.

WHAT IT DOES:
• Searches the web for merchant information
• Browses official websites and support pages
• Extracts return policies and contact details  
• Finds return portal URLs and determines process type
• Returns structured data ready for integration

REQUIREMENTS:
• OpenAI API Key (set OPENAI_API_KEY environment variable)
• Internet connection
• Python packages: langchain-openai, beautifulsoup4, requests, playwright

INPUT FORMATS:
• Merchant Name: "Amazon", "Best Buy", "Target"
• Website URL: "https://www.walmart.com"
• Domain: "costco.com"

OUTPUT:
Returns a Python dictionary with these fields:
• website: Official website URL
• return_policy: Detailed policy summary
• support_email: Customer support email
• support_url: Support page URL
• return_policy_url: Policy information page
• return_portal_url: Return submission portal
• is_via_email: True if email-based, False if web form
• research_notes: Research process details

EXAMPLES:
    python standalone_merchant_research.py "Amazon"
    python standalone_merchant_research.py "Best Buy"
    python standalone_merchant_research.py "https://www.target.com"
    python standalone_merchant_research.py "walmart.com"

TROUBLESHOOTING:
• "OPENAI_API_KEY not found": Set your API key as environment variable
• "Research failed": Check internet connection and API key validity
• "Not found" results: Try different merchant name variations
• Timeout errors: Some websites may block automated access

For more help, visit: https://platform.openai.com/docs
    """)


def main():
    """Main function to run the standalone merchant research."""
    parser = argparse.ArgumentParser(
        description='🔍 Standalone Merchant Research Tool - Research comprehensive merchant information for e-commerce return processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
📋 DETAILED USAGE GUIDE:

INPUT FORMATS:
  Merchant Name:    "Amazon", "Best Buy", "Target" 
  Website URL:      "https://www.walmart.com"
  Domain Only:      "costco.com", "target.com"

WHAT THE TOOL RESEARCHES:
  ✓ Official website and contact information
  ✓ Return policies and procedures
  ✓ Customer support details (email, phone, URLs)
  ✓ Return portal URLs for online submissions
  ✓ Return process type (email vs web form)

OUTPUT:
  Python dictionary with structured merchant data ready for integration

EXAMPLES:
  python standalone_merchant_research.py "Amazon"
  python standalone_merchant_research.py "Best Buy"  
  python standalone_merchant_research.py "https://www.target.com"
  python standalone_merchant_research.py "walmart.com"

REQUIREMENTS:
  • OPENAI_API_KEY environment variable
  • Internet connection
  • Python packages: langchain-openai, beautifulsoup4, requests, playwright

SETUP:
  1. Get OpenAI API key: https://platform.openai.com/api-keys
  2. Set environment variable: export OPENAI_API_KEY='your-key'
  3. Install packages: pip install langchain-openai beautifulsoup4 requests playwright python-dotenv
  4. Install playwright browsers: playwright install
        """
    )

    parser.add_argument(
        'merchant',
        nargs='?',
        help='Merchant name or website URL to research (e.g. "Amazon", "https://target.com")'
    )

    parser.add_argument(
        '--help-detailed',
        action='store_true',
        help='Show detailed usage guide and examples'
    )

    # Handle help cases
    if len(sys.argv) == 1:
        print("❌ Error: Merchant name or URL is required")
        print("\nQuick examples:")
        print('  python standalone_merchant_research.py "Amazon"')
        print('  python standalone_merchant_research.py "https://target.com"')
        print("\nFor detailed help: python standalone_merchant_research.py --help")
        return

    args = parser.parse_args()

    # Show detailed help
    if args.help_detailed:
        print_usage_help()
        return

    # Validate merchant argument
    if not args.merchant:
        print("❌ Error: Merchant name or URL is required")
        print("Use --help for usage information")
        return

    # Check environment setup
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not found")
        print("\nSetup instructions:")
        print("1. Get API key: https://platform.openai.com/api-keys")
        print("2. Set variable: export OPENAI_API_KEY='your-key'")
        print("3. Or add to .env file: OPENAI_API_KEY=your-key")
        return

    print("🚀 Starting merchant research...")
    print(f"📅 Timestamp: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Research the merchant
    result = research_merchant_standalone(args.merchant)

    # Print the result as a dictionary (like the original script)
    print(f"\n📊 FINAL RESULT:")
    print(result)

    # Show completion message
    if result and not result.get('error'):
        print(f"\n✅ Research completed successfully!")
        print(f"📊 Found {len([v for v in result.values() if v and v != 'Not found'])} data points")
        print("\n💡 TIP: You can copy the dictionary output above for use in your applications")
    else:
        print(f"\n❌ Research failed or incomplete")
        print("💡 Try a different merchant name or check your setup")


if __name__ == "__main__":
    main()