from datetime import date

def define_holiday(input_date) :
    
    vacation_periods = [
        (date(2025, 2, 8), date(2025, 2, 23)),  
        (date(2025, 4, 5), date(2025, 4, 21)),  
        (date(2025, 7, 5), date(2025, 8, 31)),
        (date(2025, 10, 18), date(2025, 11, 2)),
        (date(2025, 12, 20), date(2026, 1, 4)),
        (date(2026, 2, 14), date(2026, 3, 1)),
        (date(2026, 4, 11), date(2026, 4, 26)),
        (date(2026, 7, 4), date(2026, 8, 31))
    ]

    for start, end in vacation_periods:
        if start <= input_date <= end:
            return 1
        else :
            return 0
        
        
def define_public_holiday(input_date) :
    public_holidays = [
    date(2025, 1, 1),   
    date(2025, 4, 21),  
    date(2025, 5, 1),   
    date(2025, 5, 8),   
    date(2025, 5, 29),  
    date(2025, 6, 9),   
    date(2025, 7, 14),  
    date(2025, 8, 15),  
    date(2025, 11, 1),  
    date(2025, 11, 11), 
    date(2025, 12, 25),  
    date(2026, 1, 1),   
    date(2026, 4, 6),   
    date(2026, 5, 1),   
    date(2026, 5, 8),   
    date(2026, 5, 14), 
    date(2026, 5, 25),  
    date(2026, 7, 14),  
    date(2026, 8, 15), 
    date(2026, 11, 1),  
    date(2026, 11, 11), 
    date(2026, 12, 25) 
        
    ]
    if input_date in public_holidays:
            return 1
    else :
        return 0
    