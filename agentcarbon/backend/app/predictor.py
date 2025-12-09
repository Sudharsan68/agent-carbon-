from typing import List, Dict
import pandas as pd
from prophet import Prophet
import warnings
from datetime import datetime

def forecast_next_month(history: List[Dict]) -> Dict:
    """Generate forecast for next month using Prophet."""
    rows = []
    for h in history:
        date = h["fields"].get("date")
        total = h["emissions"].get("total_kgco2")
        
        # Skip if missing data
        if not date or total is None:
            continue
            
        # Try to parse date - handle various formats
        try:
            if isinstance(date, str):
                # Try common date formats
                for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"]:
                    try:
                        parsed_date = datetime.strptime(date, fmt)
                        rows.append({"ds": parsed_date, "y": float(total)})
                        break
                    except ValueError:
                        continue
            elif isinstance(date, datetime):
                rows.append({"ds": date, "y": float(total)})
        except (ValueError, TypeError):
            continue
    
    # Need at least 3 data points for Prophet
    if len(rows) < 3:
        return {"predicted_kgco2": None}

    try:
        df = pd.DataFrame(rows)
        df = df.sort_values("ds")  # Prophet requires sorted dates
        
        # Suppress Prophet warnings for cleaner logs
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            
            m = Prophet()
            m.fit(df)
            # Use 'ME' instead of deprecated 'M' for monthly frequency
            future = m.make_future_dataframe(periods=1, freq="ME")
            fcst = m.predict(future)
            pred = float(fcst.iloc[-1]["yhat"])
            
        return {"predicted_kgco2": round(pred, 2)}
    except Exception:
        # Return None if forecasting fails for any reason
        return {"predicted_kgco2": None}
