# from openrouter import OpenRouterClient
# import pandas as pd
# import re
# import json

# class CarCSVAgent:
#     """
#     Agent to query a car dataset and return filtered results along with applied filters.
#     """

#     def __init__(self, system_prompt: str = "You are a helpful assistant for car queries."):
#         # Load CSV
#         self.df = pd.read_csv("cardekho.csv")
#         # Initialize OpenRouter client
#         self.client = OpenRouterClient(system_prompt=system_prompt)

#     def query(self, user_query: str):
#         """
#         Handles user query, extracts filters using LLM, applies them on CSV,
#         and returns results along with applied filters.
#         """
#         # Ask LLM to extract filters from the user query
#         filter_prompt = f"""
#         Extract the filters for the following car query.
#         Columns available: {list(self.df.columns)}
#         Return in JSON format, keys matching column names with values or ranges.
#         User query: {user_query}
#         """
#         response = self.client.chat(messages=[{"role": "user", "content": filter_prompt}])
#         print("===="*20)
#         print(type(response))
#         print(response)
#         print("===="*20)
#         match = re.search(r'```json(.*?)```', response, re.DOTALL)

#         if match:
#             json_str = match.group(1).strip()  # extract and strip whitespace/newlines
#             filters = json.loads(json_str)   # convert to dictionary
#             print(filters)
#             print("filters read")


#         matched_filters = {}
#         unmatched_columns = []
#         for col, value in filters.items():
#             if col in self.df.columns:
#                 matched_filters[col] = value
#             else:
#                 unmatched_columns.append(col)

#         # Apply filters only on matched columns
#         filtered_df = self.df.copy()
#         for col, value in matched_filters.items():
#             # Convert numeric columns if needed
#             if isinstance(value, dict):  # Range filter
#                 if 'min' in value:
#                     filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
#                     filtered_df = filtered_df[filtered_df[col] >= value['min']]
#                 if 'max' in value:
#                     filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
#                     filtered_df = filtered_df[filtered_df[col] <= value['max']]
#             else:
#                 filtered_df = filtered_df[filtered_df[col] == value]

#         # Return filtered results, applied filters, and unmatched columns
#         return {
#             "applied_filters": matched_filters,
#             "non_matched_columns": unmatched_columns,
#             "results": filtered_df.to_dict(orient="records")
#         }


# if __name__ == "__main__":
#     agent = CarCSVAgent()
#     user_query = "Find me red cars with mileage above 15 km/l and price below 10 lakhs."
#     result = agent.query(user_query)
#     print("Applied Filters:", result["applied_filters"])
#     print("Results:", result["results"])


from .openrouter import OpenRouterClient
import pandas as pd
import re
import json
import datetime
import os 

class CarCSVAgent:
    """
    Agent to query a car dataset and return filtered results along with applied filters.
    """

    def __init__(self, system_prompt: str = "You are a helpful assistant for car queries."):
        # Load CSV
        csv_path = os.path.join(os.path.dirname(__file__), "cardekho.csv")
        self.df = pd.read_csv(csv_path)
        
        # Clean column names (remove spaces, special characters)
        self.df.columns = self.df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Convert numeric columns
        self._convert_numeric_columns()
        
        # Initialize OpenRouter client
        self.client = OpenRouterClient(system_prompt=system_prompt)
        
        # Store original column names for display
        self.original_columns = list(pd.read_csv(csv_path, nrows=0).columns)
        
    def _convert_numeric_columns(self):
        """Convert columns that should be numeric to numeric types."""
        # Common numeric columns in car datasets
        numeric_columns = ['selling_price', 'km_driven', 'mileage', 'engine', 'max_power', 
                          'year', 'seats', 'torque', 'price']
        
        for col in numeric_columns:
            if col in self.df.columns:
                # Remove commas and convert to numeric
                if self.df[col].dtype == 'object':
                    self.df[col] = self.df[col].astype(str).str.replace(',', '')
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
    
    def _preprocess_query(self, user_query: str) -> str:
        """Preprocess user query to help LLM understand better."""
        query = user_query.lower()
        
        # Map common terms to column names
        term_mapping = {
            'price': 'selling_price',
            'cost': 'selling_price',
            'lakh': 'selling_price',
            'mileage': 'mileage',
            'fuel efficiency': 'mileage',
            'kmpl': 'mileage',
            'color': 'color',  # Adjust based on your actual column
            'year': 'year',
            'model': 'year',  # Often year is used for model
            'make': 'company'  # Adjust based on your actual column
        }
        
        # Add hints to query
        actual_columns = list(self.df.columns)
        query_hint = f"\nAvailable columns: {actual_columns}"
        
        return user_query + query_hint
    
    def get_dataset_info(self):
        """Return basic info about the dataset."""
        return {
            "total_records": len(self.df),
            "columns": list(self.df.columns),
            "column_types": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            "color_column": None,
            "sample_records": self.df.head(3).to_dict(orient="records")
        }
    
    def query(self, user_query: str):
        """
        Handles user query, extracts filters using LLM, applies them on CSV,
        and returns results along with applied filters.
        """
        # Preprocess query
        enhanced_query = self._preprocess_query(user_query)
        
        # Ask LLM to extract filters from the user query
        filter_prompt = f"""
        You are an expert at extracting car search filters from natural language queries.
        
        Available columns in the dataset (use exact names as they appear below):
        {list(self.df.columns)}
        
        IMPORTANT GUIDELINES:
        1. When user mentions a color (like 'red', 'blue', 'white', 'black', etc.), 
           map it to the appropriate column:
           - If dataset has a 'color' column, use that
           - If dataset has 'car_name' or similar columns, the color might be part of the name
           - If uncertain about color column, use 'name' as fallback
        
        2. For price filters:
           - Convert lakhs to numbers (10 lakhs = 10)
           - Use 'selling_price' column
        
        3. For mileage filters:
           - Use 'mileage' column if exists
           - Use exact column name from dataset
        
        4. Return ONLY valid JSON with this structure:
           {{
             "column_name": "value",  # for exact matches
             "column_name": {{"min": value, "max": value}}  # for ranges
           }}
        
        5. ONLY include filters that can be directly applied to the dataset columns.
        
        User query: "{user_query}"
        
        Extract and return JSON filters:
        """
        
        response = self.client.chat(messages=[{"role": "user", "content": filter_prompt}])
        
        print("===="*20)
        print("LLM Response:", response)
        print("===="*20)
        
        # Try to extract JSON
        try:
            # Try to find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                filters = json.loads(json_str)
            else:
                # If no JSON found, try to parse entire response
                filters = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {
                "error": "Failed to parse filters from LLM response",
                "llm_response": response,
                "results": []
            }
        
        print("Parsed filters:", filters)
        
        # Apply filters
        filtered_df = self.df.copy()
        applied_filters = {}
        unmatched_columns = []
        
        for col, value in filters.items():
            # Normalize column name
            col_lower = col.lower().strip().replace(' ', '_')
            
            if col_lower in self.df.columns:
                applied_filters[col] = value
                
                if isinstance(value, dict):  # Range filter
                    if 'min' in value:
                        min_val = value['min']
                        # Convert lakhs to actual numbers if needed
                        if 'lakh' in str(user_query).lower() and col_lower == 'selling_price':
                            min_val = min_val * 100000
                        filtered_df = filtered_df[filtered_df[col_lower] >= min_val]
                    
                    if 'max' in value:
                        max_val = value['max']
                        # Convert lakhs to actual numbers if needed
                        if 'lakh' in str(user_query).lower() and col_lower == 'selling_price':
                            max_val = max_val * 100000
                        filtered_df = filtered_df[filtered_df[col_lower] <= max_val]
                
                elif isinstance(value, str):  # Exact match filter
                    # Handle color/name search
                    if 'red' in value.lower():
                        # Try to find color-related columns
                        color_cols = [c for c in self.df.columns if 'color' in c or 'name' in c]
                        if color_cols:
                            # Search in all possible columns
                            mask = pd.Series(False, index=filtered_df.index)
                            for color_col in color_cols:
                                mask = mask | filtered_df[color_col].astype(str).str.contains('red', case=False, na=False)
                            filtered_df = filtered_df[mask]
                        else:
                            # Fall back to string search in all columns
                            mask = filtered_df.apply(
                                lambda row: row.astype(str).str.contains('red', case=False).any(), 
                                axis=1
                            )
                            filtered_df = filtered_df[mask]
                    else:
                        # Regular exact match
                        filtered_df = filtered_df[filtered_df[col_lower].astype(str).str.contains(value, case=False, na=False)]
                
                elif isinstance(value, (int, float)):  # Numeric exact match
                    filtered_df = filtered_df[filtered_df[col_lower] == value]
            else:
                unmatched_columns.append(col)
        
        # Clean results for display
        results = filtered_df.head(50).to_dict(orient="records")  # Limit to 50 results
        
        # Format price in lakhs for readability
        for record in results:
            if 'selling_price' in record and record['selling_price']:
                record['selling_price_lakhs'] = record['selling_price'] / 100000
        
        return {
            "query": user_query,
            "applied_filters": applied_filters,
            "non_matched_columns": unmatched_columns,
            "total_results": len(filtered_df),  # NOT 'num_results'
            "returned_results": len(results),
            "timestamp": datetime.datetime.now().isoformat(),
            "results": results
        }


def debug_dataset(csv_path=None):
    """Debug function to explore the dataset."""
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), "cardekho.csv")
    df = pd.read_csv(csv_path)
    
    print("Dataset Info:")
    print(f"Shape: {df.shape}")
    print("\nColumns:")
    for col in df.columns:
        print(f"  - {col}: {df[col].dtype}")
        if df[col].dtype == 'object':
            print(f"    Sample values: {df[col].dropna().unique()[:5]}")
    
    print("\nFirst few rows:")
    print(df.head())
    
    return df


if __name__ == "__main__":
    # First debug the dataset
    print("=== DEBUGGING DATASET ===")
    df = debug_dataset("cardekho.csv")
    
    # Then run the agent
    print("\n=== RUNNING AGENT ===")
    agent = CarCSVAgent()
    
    # Test query
    user_query = "Find me red cars with mileage above 15 km/l and price below 10 lakhs."
    result = agent.query(user_query)
    
    print("\n=== RESULTS ===")
    print(f"Applied Filters: {result['applied_filters']}")
    print(f"Number of results: {result['num_results']}")
    print(f"First few results: {result['results'][:5]}")