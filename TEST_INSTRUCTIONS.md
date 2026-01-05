# Test Instructions - Very Lenient Tracking

## Settings Applied

**File**: `local_backend/frame_api.py`

```python
similarity_threshold=0.45   # Very lenient (was 0.55)
max_disappeared=200         # 66 seconds persistence (was 100)
update_alpha=0.85          # More adaptive (was 0.9)
```

## How to Test

### 1. Wait for Server to Reload
The server auto-reloads. Wait 5 seconds.

### 2. Test Extension

1. **Open extension**
2. **Click "Stop"** (if capturing)
3. **Click "Start Capture"** (resets tracker with new settings)
4. **Select BTS video tab**
5. **Play video**

### 3. Expected Output

```
✅ Face tracker reset
✅ Face tracker initialized (similarity=0.45, max_disappeared=200)
✅ Capture started
✅ Frame: 9 faces detected [P1-P9]
✅ Frame: 9 faces detected [P1-P9]
✅ Frame: 9 faces detected [P1-P9]
```

## What Changed

- **0.45 threshold**: Very lenient - will match faces even with significant movement
- **200 frames**: 66 seconds of persistence - people can disappear for over a minute
- **0.85 alpha**: Embeddings adapt faster to changes

## If Still Not Working

The issue may be that the BTS video has people moving so much that face embeddings change too drastically. In that case, the only solution would be to:

1. Process more frames (reduce FRAME_SKIP from 10 to 5)
2. Or accept that IDs will change when people move significantly

But try this first - these are very lenient settings.
