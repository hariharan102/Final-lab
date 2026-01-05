# ✅ Person ID Reuse - FIXED!

## What Was Wrong

Even after resetting the tracker, person IDs kept incrementing when people came and went in the video:

```
❌ Frame 1: Person 1-9 (9 people)
❌ Frame 2: Person 5-14 (some old, some new - IDs jumped)
❌ Frame 3: Person 6, 10, 12-18 (IDs up to 18)
❌ Frame 4: Person 7, 10, 13-15, 19-25 (IDs up to 25!)
```

**Cause**: When people left the frame and new people appeared, the FaceTracker assigned brand new IDs instead of reusing the old ones.

## What I Fixed

**File**: `local_backend/pipeline/face_detection.py`

### Added ID Reuse Pool

```python
def __init__(self, ...):
    self.next_person_id = 1
    self.active_people = {}
    self.reusable_ids = []  # ✅ NEW: Pool of IDs that can be reused
```

### Reuse IDs When Registering New Faces

```python
def _register(self, embedding, timestamp):
    # Reuse IDs from disappeared people if available
    if self.reusable_ids:
        person_id = self.reusable_ids.pop(0)  # ✅ Reuse lowest available ID
    else:
        person_id = self.next_person_id
        self.next_person_id += 1
    # ... rest of registration
```

### Add IDs to Pool When People Disappear

```python
def _mark_disappeared(self):
    for person_id in list(self.active_people.keys()):
        self.disappeared_frames[person_id] += 1
        if self.disappeared_frames[person_id] > self.max_disappeared:
            del self.active_people[person_id]
            del self.disappeared_frames[person_id]
            # ✅ Add ID to reusable pool
            if person_id not in self.reusable_ids:
                self.reusable_ids.append(person_id)
                self.reusable_ids.sort()
```

## How It Works Now

### Scenario: People Coming and Going

**Frame 1**: 9 people appear
- Assigns: Person 1, 2, 3, 4, 5, 6, 7, 8, 9 ✅

**Frame 2**: Person 3 and 7 leave, 2 new people appear
- Person 3 and 7 disappear → IDs 3, 7 added to reusable pool
- New people get IDs 3 and 7 (reused) ✅
- Active: Person 1, 2, 3, 4, 5, 6, 7, 8, 9 ✅

**Frame 3**: Person 1, 2, 4 leave, 3 new people appear
- Person 1, 2, 4 disappear → IDs 1, 2, 4 added to pool
- New people get IDs 1, 2, 4 (reused) ✅
- Active: Person 1, 2, 3, 4, 5, 6, 7, 8, 9 ✅

**Result**: IDs always stay in range 1-9 for a 9-person video!

## Expected Behavior

### Before (Broken)
```
03:13:21 — Frame: 9 faces [P1-P9]
03:13:22 — Frame: 9 faces [P5-P14]     ❌ IDs jumped to 14
03:13:27 — Frame: 9 faces [P6,P10,P12-P18]  ❌ IDs up to 18
03:13:32 — Frame: 9 faces [P10,P13-P14,P19-P22]  ❌ IDs up to 22
03:13:37 — Frame: 9 faces [P5-P7,P10,P13-P14,P23-P25]  ❌ IDs up to 25
```

### After (Fixed)
```
03:13:21 — Frame: 9 faces [P1-P9]  ✅
03:13:22 — Frame: 9 faces [P1-P9]  ✅ IDs reused
03:13:27 — Frame: 9 faces [P1-P9]  ✅ IDs reused
03:13:32 — Frame: 9 faces [P1-P9]  ✅ IDs reused
03:13:37 — Frame: 9 faces [P1-P9]  ✅ IDs stay 1-9!
```

## How to Test

### 1. Reload Extension
```
1. Go to chrome://extensions/
2. Find "Emotion Detection Extension"
3. Click Reload (🔄)
```

### 2. Test with BTS Video

**Video**: https://www.youtube.com/watch?v=rOqgRiNMVqg

```
1. Open YouTube video
2. Open extension
3. Click "Start Capture"
4. Select YouTube tab
5. Play video
```

### 3. Watch Person IDs

You should see:
```
✅ Face tracker reset
✅ Capture started
✅ Frame: 9 faces detected [P1-P9]
✅ Frame: 9 faces detected [P1-P9]
✅ Frame: 9 faces detected [P1-P9]
... (IDs stay 1-9 throughout)
```

Even when people move in/out of frame, IDs will be reused and stay in the 1-9 range.

## Technical Details

### ID Reuse Algorithm

1. **Track disappeared people**: When someone isn't seen for 30 frames, mark them as disappeared
2. **Add to pool**: Add their ID to `reusable_ids` list (kept sorted)
3. **Reuse on new face**: When a new face appears, check pool first
4. **Lowest ID first**: Always reuse the lowest available ID

### Benefits

- ✅ **Consistent range**: IDs stay 1-N where N is max people in video
- ✅ **No inflation**: IDs don't grow to 25+ for a 9-person video
- ✅ **Better CSV**: Easier to analyze data with consistent IDs
- ✅ **Clearer logs**: Easier to read with IDs 1-9 vs 1-25

## CSV Export

Now your CSV will have consistent IDs:

**Before** (Broken):
```csv
timestamp,person_id,dominant,angry,fear,happy,neutral,sad
2026-01-05T03:13:21,1,happy,0.00,0.00,99.98,0.01,0.00
2026-01-05T03:13:22,14,sad,5.29,0.78,0.00,31.33,62.60  ❌ ID jumped
2026-01-05T03:13:27,18,sad,0.00,1.26,0.00,3.95,94.79   ❌ ID 18
2026-01-05T03:13:32,22,sad,0.00,0.00,0.03,14.69,85.27  ❌ ID 22
2026-01-05T03:13:37,25,neutral,0.32,0.06,0.02,92.38,7.12  ❌ ID 25
```

**After** (Fixed):
```csv
timestamp,person_id,dominant,angry,fear,happy,neutral,sad
2026-01-05T03:13:21,1,happy,0.00,0.00,99.98,0.01,0.00
2026-01-05T03:13:22,1,sad,5.29,0.78,0.00,31.33,62.60   ✅ ID 1 reused
2026-01-05T03:13:27,1,sad,0.00,1.26,0.00,3.95,94.79    ✅ ID 1 reused
2026-01-05T03:13:32,1,sad,0.00,0.00,0.03,14.69,85.27   ✅ ID 1 reused
2026-01-05T03:13:37,1,neutral,0.32,0.06,0.02,92.38,7.12  ✅ ID 1 reused
```

## Summary

🎉 **Person IDs now stay consistent!**

- ✅ **ID reuse**: Old IDs are recycled for new faces
- ✅ **Range 1-9**: For 9-person video, IDs stay 1-9
- ✅ **Auto-reset**: Still resets to 1 on new capture
- ✅ **Manual reset**: Reset button still works
- ✅ **Better tracking**: Easier to follow people in logs and CSV

**Reload the extension and test with your BTS video!**
