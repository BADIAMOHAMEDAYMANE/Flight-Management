"""
Response Processor Utilities
Handles processing of AI responses and special formatting
"""

import json


class ResponseProcessor:
    """Utility class for processing bot responses"""
    
    @staticmethod
    def process_bot_response(text):
        """
        Process bot response to extract special formatting markers.
        
        Args:
            text (str): Raw response text from AI
        
        Returns:
            dict: Processed response with extracted destination cards and suggestion buttons
        
        This function extracts:
        - Destination cards: {destination_card}Paris{/destination_card}
        - Suggestion buttons: {suggest_buttons}["Button 1", "Button 2"]{/suggest_buttons}
        """
        
        # Extract destination cards
        destination_cards = []
        dest_card_start = "{destination_card}"
        dest_card_end = "{/destination_card}"
        
        start_idx = 0
        while True:
            start = text.find(dest_card_start, start_idx)
            if start == -1:
                break
            
            end = text.find(dest_card_end, start)
            if end == -1:
                break
            
            # Extract the destination name
            destination_name = text[start + len(dest_card_start):end].strip()
            destination_cards.append(destination_name)
            
            # Move to the next position
            start_idx = end + len(dest_card_end)
        
        # Extract suggestion buttons
        suggestion_buttons = []
        suggest_start = "{suggest_buttons}"
        suggest_end = "{/suggest_buttons}"
        
        start_idx = 0
        while True:
            start = text.find(suggest_start, start_idx)
            if start == -1:
                break
            
            end = text.find(suggest_end, start)
            if end == -1:
                break
            
            # Extract the buttons JSON string
            buttons_str = text[start + len(suggest_start):end].strip()
            try:
                buttons = json.loads(buttons_str)
                suggestion_buttons = buttons
            except:
                pass  # Ignore JSON parse errors
            
            # Move to the next position
            start_idx = end + len(suggest_end)
        
        # Remove the special markers from the text for clean display
        clean_text = text.replace(dest_card_start, "**").replace(dest_card_end, "**")
        clean_text = clean_text.replace(suggest_start, "").replace(suggest_end, "")
        
        # Try to clean up any JSON artifacts that might remain
        try:
            json_start = clean_text.find("[")
            json_end = clean_text.find("]", json_start)
            if json_start != -1 and json_end != -1:
                json_str = clean_text[json_start:json_end+1]
                if all(x in json_str for x in ['"', ',']):  # Looks like JSON
                    clean_text = clean_text.replace(json_str, "")
        except:
            pass  # Ignore cleanup errors
        
        return {
            "text": clean_text,
            "destinationCards": destination_cards,
            "suggestionButtons": suggestion_buttons
        }
    
    @staticmethod
    def extract_json_from_ai_response(response_text):
        """
        Extract JSON content from AI response, handling markdown code blocks.
        
        Args:
            response_text (str): Raw AI response
        
        Returns:
            dict: Parsed JSON data or None if parsing fails
        """
        try:
            # Handle potential markdown code block formatting
            if "```json" in response_text:
                # Extract content between markdown code blocks
                start = response_text.find("```json") + len("```json")
                end = response_text.rfind("```")
                json_content = response_text[start:end].strip()
            elif "```" in response_text:
                # Extract content between generic code blocks
                start = response_text.find("```") + len("```")
                end = response_text.rfind("```")
                json_content = response_text[start:end].strip()
            else:
                # Use the response as is
                json_content = response_text
            
            # Parse the JSON
            return json.loads(json_content)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return None
        except Exception as e:
            print(f"Error extracting JSON: {e}")
            return None