# RescueTime macOS status bar

Put your API key in `credentials.json`, in the following format:
```json
{
    "rescuetime": {
        "Key": "..."
    }
}
```

Run the status bar app with:
```python
python app.py
```

This will display the productivity pulse, and automatically update the current day's
score. Unlike the dashboard, this pulse also includes mobile time.

## Requirements

- pandas
- numpy
- rumps
- json

## Thanks

- Data download code was based off of https://github.com/libertyequalitydata/RescueTime
