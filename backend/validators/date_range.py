from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict

class DateRangeValidator:
    # Constants for date range validation
    MAX_DAYS_PAST = 7
    MAX_DAYS_FUTURE = 5
    MAX_RANGE_DAYS = 5
    DATE_FORMAT = '%Y-%m-%d'

    @classmethod
    def validate(cls, start_date: str, end_date: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Validate a date range according to the application rules.
        
        Args:
            start_date: Start date string in YYYY-MM-DD format
            end_date: End date string in YYYY-MM-DD format
            
        Returns:
            Tuple containing:
            - Boolean indicating if date range is valid
            - String message describing the validation result
            - Dictionary with parsed dates if valid, None if invalid
        """
        try:
            # Parse dates
            start = datetime.strptime(start_date, cls.DATE_FORMAT).date()
            end = datetime.strptime(end_date, cls.DATE_FORMAT).date()
            
            today = datetime.now().date()
            max_past_date = today - timedelta(days=cls.MAX_DAYS_PAST)
            max_future_date = today + timedelta(days=cls.MAX_DAYS_FUTURE)
            
            # Validate date order
            if start > end:
                return False, "Start date must be before or equal to end date", None
                
            # Validate date range size
            range_days = (end - start).days
            if range_days > cls.MAX_RANGE_DAYS:
                return False, f"Date range cannot exceed {cls.MAX_RANGE_DAYS} days", None
                
            # Validate against past limit
            if start < max_past_date:
                return False, f"Start date cannot be more than {cls.MAX_DAYS_PAST} days in the past", None
                
            # Validate against future limit
            if end > max_future_date:
                return False, f"End date cannot be more than {cls.MAX_DAYS_FUTURE} days in the future", None
                
            # Return validated dates
            return True, "Valid date range", {
                'start_date': start,
                'end_date': end,
                'range_days': range_days + 1  # Include both start and end dates
            }
            
        except ValueError as e:
            return False, f"Invalid date format. Use {cls.DATE_FORMAT}", None

    @classmethod
    def format_for_display(cls, date_obj: datetime.date) -> Dict:
        """
        Format a date for display purposes.
        
        Args:
            date_obj: A datetime.date object
            
        Returns:
            Dictionary containing formatted date information
        """
        return {
            'iso': date_obj.isoformat(),
            'display': date_obj.strftime('%B %d, %Y'),
            'short': date_obj.strftime('%m/%d/%Y')
        }

    @classmethod
    def get_valid_range_bounds(cls) -> Dict:
        """
        Get the current valid date range bounds.
        
        Returns:
            Dictionary containing the earliest and latest valid dates
        """
        today = datetime.now().date()
        return {
            'earliest_date': (today - timedelta(days=cls.MAX_DAYS_PAST)).isoformat(),
            'latest_date': (today + timedelta(days=cls.MAX_DAYS_FUTURE)).isoformat(),
            'today': today.isoformat(),
            'max_range_days': cls.MAX_RANGE_DAYS
        }

    @classmethod
    def generate_date_range(cls, start_date: datetime.date, end_date: datetime.date) -> list:
        """
        Generate a list of dates between start and end dates (inclusive).
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of formatted dates in the range
        """
        date_list = []
        current_date = start_date
        
        while current_date <= end_date:
            date_list.append(cls.format_for_display(current_date))
            current_date += timedelta(days=1)
            
        return date_list