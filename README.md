# MHSystem
bbbbb
定数
	会社CD
		NTPS = 1
		トーテック = 2
		ITC = 99

main
	会社判別
	各社　pdf読み込み　→　フォーマット合わせが目的
	ジョブカンデータ読み込み
	比較　完全一致比較
	ファイル名作成　（出向先_氏名_yyyyMMdd.csv）
	出力
	ポップアップ出力（おわったよ。差異無いよ。三日分違うよ（9/10,9/11,9/12））

会社判別
	会社名を定数の会社CDに置き換え

各社pdf読み込み
	引数　
		pdfデータ、会社CD
	戻り値 pandasデータフレーム
        社員名 姓
    	社員名 名　NULL OK
        日付 datetime.date(yyyy,MM,dd) => yyyy-MM-dd
        実働時間 HH:mm
            （warning 樋口 HH:mm　のほうがいいと思います）=> 村瀬 OK,休憩時間も準じます
        開始時間 HH:mm　NULL OK
        終了時間 HH:mm　NULL OK
        休憩時間 HH:mm　NULL OK
        備考 string　NULL OK
	
ジョブカンデータの読み込み

比較

出力　excel or CSV


ファイル構成
main .py
higuti.py
higuti_sanityse.py
higuti_util.py
murase.py
