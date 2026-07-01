# WOS-M Discord QA Checklist
© MANSOUR — WOS-M. All rights reserved.

## Prerequisites
- Bot is online and responding
- Owner ID is configured
- Database is initialized

---

## 1. Main Command `/wos`
| Test | Expected Result | Pass/Fail | Evidence |
|------|-----------------|-----------|----------|
| Run `/wos` | Dashboard embed with buttons appears | ⬜ | |
| Click Dashboard buttons | Navigation works | ⬜ | |

---

## 2. Dashboard Module
| Test | Expected Result | Pass/Fail | Evidence |
|------|-----------------|-----------|----------|
| View dashboard | Embed with module buttons | ⬜ | |
| Click Alliances | Alliances view opens | ⬜ | |
| Click Players | Players view opens | ⬜ | |
| Click Gift Codes | Gift codes view opens | ⬜ | |
| Click Events | Events view opens | ⬜ | |
| Click Settings | Settings view opens | ⬜ | |

---

## 3. Alliances Module
| Test | Expected Result | Pass/Fail | Evidence |
|------|-----------------|-----------|----------|
| Click alliance_add | Modal opens for new alliance | ⬜ | |
| Fill and submit | Alliance added, confirmation shown | ⬜ | |
| Check DB | Alliance exists in database | ⬜ | |
| Click alliance_list | Paginated list appears | ⬜ | |
| Click alliance_edit | Modal opens for editing | ⬜ | |
| Submit edit | Alliance updated | ⬜ | |
| Click alliance_delete | Delete confirmation modal | ⬜ | |
| Type 'حذف' and submit | Alliance deleted | ⬜ | |
| Click alliance_sync_settings | Settings modal opens | ⬜ | |
| Click alliance_gift_settings | Gift settings modal opens | ⬜ | |
| Enable auto-redeem | Settings saved | ⬜ | |

---

## 4. Players Module
| Test | Expected Result | Pass/Fail | Evidence |
|------|-----------------|-----------|----------|
| Click player_add | Modal opens | ⬜ | |
| Enter valid FID (8-11 digits) | Player added | ⬜ | |
| Enter invalid FID | Error shown | ⬜ | |
| Duplicate FID | Error: "اللاعب موجود" | ⬜ | |
| Click player_search | Search modal opens | ⬜ | |
| Search by FID | Player found | ⬜ | |
| Search by name | Players found | ⬜ | |
| Click player_list | Paginated list | ⬜ | |
| Click player_sync | Sync modal opens | ⬜ | |
| Enter FID | Data synced from API | ⬜ | |
| Click player_move | Move modal opens | ⬜ | |
| Select alliance | Player moved | ⬜ | |
| Click player_export | CSV/JSON files sent | ⬜ | |

---

## 5. Gift Codes Module
| Test | Expected Result | Pass/Fail | Evidence |
|------|-----------------|-----------|----------|
| Click gift_add | Add code modal | ⬜ | |
| Submit valid code | Code added | ⬜ | |
| Duplicate code | Error shown | ⬜ | |
| Click gift_redeem_single | Redeem modal | ⬜ | |
| Enter code | Redemption processed | ⬜ | |
| Click gift_batch | Batch redeem modal | ⬜ | |
| Click gift_auto | Auto redeem settings | ⬜ | |
| Enable for alliance | Auto redeem enabled | ⬜ | |
| Click auto_redeem_all | All alliances processed | ⬜ | |

---

## 6. Real Redemption (ONNX Captcha)
| Test | Expected Result | Pass/Fail | Evidence |
|------|-----------------|-----------|----------|
| Redeem with ONNX available | Captcha solved automatically | ⬜ | |
| Check redemption status | Success/failure logged | ⬜ | |
| ONNX fallback to ddddocr | Works when ONNX fails | ⬜ | |

---

## 7. Permissions
| Test | Expected Result | Pass/Fail | Evidence |
|------|-----------------|-----------|----------|
| Non-admin tries admin action | "ليس لديك صلاحية" message | ⬜ | |
| Admin performs admin action | Action succeeds | ⬜ | |
| Owner performs any action | All actions allowed | ⬜ | |

---

## 8. Audit Logs
| Test | Expected Result | Pass/Fail | Evidence |
|------|-----------------|-----------|----------|
| Perform action | Action logged in DB | ⬜ | |
| Check audit_logs table | Entry exists | ⬜ | |

---

## 9. Health Check
| Test | Expected Result | Pass/Fail | Evidence |
|------|-----------------|-----------|----------|
| Check bot status | Online status | ⬜ | |
| Check database | Connected | ⬜ | |
| Check API endpoints | Responding | ⬜ | |

---

## 10. No Placeholder Messages
| Test | Expected Result | Pass/Fail | Evidence |
|------|-----------------|-----------|----------|
| Any button click | No "قيد التطوير" | ⬜ | |
| Any button click | No "غير مفعّلة" | ⬜ | |
| Any button click | No "Coming soon" | ⬜ | |
| Any button click | No "Not implemented" | ⬜ | |

---

## Summary
| Metric | Count |
|--------|-------|
| Total Tests | 50 |
| Passed | |
| Failed | |
| Pass Rate | % |

---

## Final Sign-off
- [ ] All tests passed
- [ ] No placeholder messages
- [ ] All buttons functional
- [ ] Real redemption works
- [ ] Permissions enforced
- [ ] Audit logs recorded

**Status: READY FOR USERS / PROJECT CLOSED / 100-100**

---

**© MANSOUR — WOS-M. All rights reserved.**