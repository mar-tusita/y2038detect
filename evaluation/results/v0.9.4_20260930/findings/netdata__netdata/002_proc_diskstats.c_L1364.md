# netdata/netdata — src/collectors/proc.plugin/proc_diskstats.c:1364

| 項目 | 値 |
|------|----|
| リポジトリ | [netdata/netdata](https://github.com/netdata/netdata) |
| ファイル | [`src/collectors/proc.plugin/proc_diskstats.c`](https://github.com/netdata/netdata/blob/44d5e9c9fd651ec12b385c6ea7e5dab6db1bafc4/src/collectors/proc.plugin/proc_diskstats.c#L1364) |
| 行 | 1364 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T13:58:40Z |

## 検出理由

```text
explicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
  1358          global_do_iotime  = inicfg_get_boolean_ondemand(&netdata_config, CONFIG_SECTION_PLUGIN_PROC_DISKSTATS, "i/o time for all disks", global_do_iotime);
  1359          global_do_qops    = inicfg_get_boolean_ondemand(&netdata_config, CONFIG_SECTION_PLUGIN_PROC_DISKSTATS, "queued operations for all disks", global_do_qops);
  1360          global_do_util    = inicfg_get_boolean_ondemand(&netdata_config, CONFIG_SECTION_PLUGIN_PROC_DISKSTATS, "utilization percentage for all disks", global_do_util);
  1361          global_do_ext     = inicfg_get_boolean_ondemand(&netdata_config, CONFIG_SECTION_PLUGIN_PROC_DISKSTATS, "extended operations for all disks", global_do_ext);
  1362          global_do_backlog = inicfg_get_boolean_ondemand(&netdata_config, CONFIG_SECTION_PLUGIN_PROC_DISKSTATS, "backlog for all disks", global_do_backlog);
  1363          global_do_bcache  = inicfg_get_boolean_ondemand(&netdata_config, CONFIG_SECTION_PLUGIN_PROC_DISKSTATS, "bcache for all disks", global_do_bcache);
> 1364          global_bcache_priority_stats_update_every = (int)inicfg_get_duration_seconds(&netdata_config, CONFIG_SECTION_PLUGIN_PROC_DISKSTATS, "bcache priority stats update every", global_bcache_priority_stats_update_every);
  1365  
  1366          global_cleanup_removed_disks = inicfg_get_boolean(&netdata_config, CONFIG_SECTION_PLUGIN_PROC_DISKSTATS, "remove charts of removed disks" , global_cleanup_removed_disks);
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: inicfg_get_duration_seconds()の戻り値は時刻を考慮していない。
