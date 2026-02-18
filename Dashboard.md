# 🤖 AI Employee Dashboard
**Last Updated:** 2026-02-13 15:13:03

## 🖥️ System Health
| Metric | Usage | Status |
| :--- | :--- | :--- |
| **CPU** | 12.3% | 🟢 Good |
| **RAM** | 88.2% | 🔴 High |
| **Disk** | 48.6% | 🟢 Good |

## 📂 Workflow Queue
| Folder | Files | Status |
| :--- | :--- | :--- |
| 📥 **Inbox** | 0 | Empty |
| ⚠️ **Needs Action** | 0 | Clear |
| ⏳ **Pending Approval** | 0 | Clear |
| ✅ **Approved** | 0 | - |
| 🏁 **Done** | 5 | - |
| ❌ **Failed** | 7 | **CHECK LOGS** |

## 📅 Upcoming Schedule
| Task | Next Run | Interval |
| :--- | :--- | :--- |
| `twitter_check` | **03:25:45** | Job(interval=3, unit=hours, do=twitter_check, args=(), kwargs={}) |
| `linkedin_check` | **06:25:45** | Job(interval=6, unit=hours, do=linkedin_check, args=(), kwargs={}) |
| `whatsapp_check` | **02:25:45** | Job(interval=2, unit=hours, do=whatsapp_check, args=(), kwargs={}) |
| `email_check` | **01:25:45** | Job(interval=1, unit=hours, do=email_check, args=(), kwargs={}) |
| `content_generation` | **09:00:00** | Job(interval=1, unit=days, do=content_generation, args=(), kwargs={}) |

## 📜 Recent Activity
| Time | Status | Platform | Log File |
| :--- | :---: | :--- | :--- |
| 00:26:28 | ✅ | linkedin | success_20260211_002628_VALIDATION_LINKEDIN_20260211_002554.json |
| 00:26:00 | ❌ | linkedin | failed_20260211_002600_VALIDATION_LINKEDIN_20260211_002554.json |
| 00:25:57 | ❌ | twitter | failed_20260211_002557_VALIDATION_TWITTER_20260211_002554.json |
| 00:25:56 | ❌ | twitter | failed_20260211_002556_VALIDATION_TWITTER_20260211_002554.json |
| 00:08:47 | ✅ | linkedin | success_20260211_000847_VALIDATION_LINKEDIN_20260211_000824.json |
| 00:08:29 | ✅ | linkedin | success_20260211_000829_VALIDATION_LINKEDIN_20260211_000824.json |
| 00:08:27 | ❌ | twitter | failed_20260211_000827_VALIDATION_TWITTER_20260211_000824.json |
| 00:08:26 | ❌ | twitter | failed_20260211_000826_VALIDATION_TWITTER_20260211_000824.json |
| 23:44:26 | ✅ | linkedin | success_20260210_234426_VALIDATION_LINKEDIN_20260210_234401.json |
| 23:44:05 | ✅ | linkedin | success_20260210_234405_VALIDATION_LINKEDIN_20260210_234401.json |

---
> *This dashboard updates automatically when `scripts/update_dashboard.py` runs.*



## 2026-02-13 15:51:33 -  Linkedin Failed

**File**: LINKEDIN_POST_post_20260213_152055.md
**Platform**: linkedin
**Status**: Failed to post
**Type**: linkedin_post_approval
**Error**: Not logged in to LinkedIn. Please login first.


---


## 2026-02-13 15:57:18 -  Linkedin Failed

**File**: LINKEDIN_POST_post_20260213_152055.md
**Platform**: linkedin
**Status**: Failed to post
**Type**: linkedin_post_approval
**Error**: Not logged in to LinkedIn. Please login first.


---


## 2026-02-13 15:59:11 -  Linkedin Posted

**File**: LINKEDIN_POST_post_20260213_152055.md
**Platform**: linkedin
**Status**: Successfully posted
**Type**: linkedin_post_approval



---


## 2026-02-13 16:03:02 -  Facebook Posted

**File**: FACEBOOK_TEST_POST.md
**Platform**: facebook
**Status**: Successfully posted
**Type**: facebook_post



---


## 2026-02-13 16:03:06 -  Whatsapp Failed

**File**: WHATSAPP_TEST_MSG.md
**Platform**: whatsapp
**Status**: Failed to post
**Type**: whatsapp_message
**Error**: expected string or bytes-like object, got 'int'


---


## 2026-02-13 16:05:37 -  Whatsapp Failed

**File**: WHATSAPP_REQUEST_MSG.md
**Platform**: whatsapp
**Status**: Failed to post
**Type**: whatsapp_message
**Error**: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("button[aria-label=\"Send\"]") to be visible



---


## 2026-02-13 16:20:49 -  Whatsapp Posted

**File**: WHATSAPP_REQUEST_MSG_RETRY.md
**Platform**: whatsapp
**Status**: Successfully posted
**Type**: whatsapp_message



---


## 2026-02-13 16:22:39 -  Email Posted

**File**: EMAIL_TEST_MSG.md
**Platform**: email
**Status**: Successfully posted
**Type**: email



---


## 2026-02-13 16:27:58 -  Whatsapp Posted

**File**: WHATSAPP_TEST_MSG.md
**Platform**: whatsapp
**Status**: Successfully posted
**Type**: whatsapp_message



---


## 2026-02-14 01:12:52 -  Linkedin Posted

**File**: VALIDATION_LINKEDIN_20260211_002554.md
**Platform**: linkedin
**Status**: Successfully posted
**Type**: linkedin_post



---


## 2026-02-14 01:13:48 -  Whatsapp Posted

**File**: WHATSAPP_REQUEST_MSG.md
**Platform**: whatsapp
**Status**: Successfully posted
**Type**: whatsapp_message



---


## 2026-02-14 01:17:01 -  Whatsapp Posted

**File**: WHATSAPP_DEMO_MSG.md
**Platform**: whatsapp
**Status**: Successfully posted
**Type**: whatsapp_message



---


## 2026-02-14 01:22:18 -  Facebook Posted

**File**: FACEBOOK_DEMO_POST.md
**Platform**: facebook
**Status**: Successfully posted
**Type**: facebook_post



---


## 2026-02-16 20:30:25 -  Unknown Failed

**File**: FACEBOOK_POST_TEST.md
**Platform**: unknown
**Status**: Failed to post
**Type**: facebook_post
**Error**: Could not submit post: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("div[aria-label=\"Next\"]").first
    - locator resolved to <div tabindex="0" role="button" aria-label="Next" class="x1i10hfl xjbqb8w x1ejq31n x18oe1m7 x1sy0etr xstzfhl x972fbf x10w94by x1qhh985 x14e42zd x1ypdohk x3ct3a4 xdj266r x14z9mp xat24cr x1lziwak xexx8yu xyri2b x18d9i69 x1c1uobl x16tdsg8 x1hl2dhg xggy1nq x1fmog5m xu25z0z x140muxe xo1y3bh x87ps6o x1lku1pv x1a2a7pz x9f619 x3nfvp2 xdt5ytf xl56j7k x1n2onr6 xh8yej3">…</div>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <span dir="auto" class="xdmh292 x15dsfln x140p0ai x1gufx9m x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x193iq5w xeuugli x13faqbe x1vvkbs x1yc453h x1lliihq xi81zsa xlh3980 xvmahel x1x9mg3 xo1l8bm">196K posts</span> from <div>…</div> subtree intercepts pointer events
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <span dir="auto" class="xdmh292 x15dsfln x140p0ai x1gufx9m x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x193iq5w xeuugli x13faqbe x1vvkbs x1yc453h x1lliihq xi81zsa xlh3980 xvmahel x1x9mg3 xo1l8bm">196K posts</span> from <div>…</div> subtree intercepts pointer events
    - retrying click action
      - waiting 100ms
    57 × waiting for element to be visible, enabled and stable
       - element is visible, enabled and stable
       - scrolling into view if needed
       - done scrolling
       - <span dir="auto" class="xdmh292 x15dsfln x140p0ai x1gufx9m x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x193iq5w xeuugli x13faqbe x1vvkbs x1yc453h x1lliihq xi81zsa xlh3980 xvmahel x1x9mg3 xo1l8bm">196K posts</span> from <div>…</div> subtree intercepts pointer events
     - retrying click action
       - waiting 500ms



---


## 2026-02-16 20:31:33 -  Generic Posted

**File**: WHATSAPP_TEST.md
**Platform**: generic
**Status**: Successfully posted
**Type**: unknown



---


## 2026-02-16 20:38:02 -  Linkedin Posted

**File**: LINKEDIN_POST_TEST.md
**Platform**: linkedin
**Status**: Successfully posted
**Type**: linkedin_post_approval



---


## 2026-02-16 20:39:46 -  Whatsapp Failed

**File**: WHATSAPP_TEST_MSG.md
**Platform**: whatsapp
**Status**: Failed to post
**Type**: whatsapp_message
**Error**: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("button[aria-label=\"Send\"]") to be visible



---


## 2026-02-16 20:41:39 -  Whatsapp Failed

**File**: WHATSAPP_TEST_MSG.md
**Platform**: whatsapp
**Status**: Failed to post
**Type**: whatsapp_message
**Error**: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("button[aria-label=\"Send\"]") to be visible



---
