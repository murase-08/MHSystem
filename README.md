# MHSystem
bbbbb
定数
	会社CD
		<!-- NTPS = 1
		トーテック = 2
		ITC = 99 -->

		ジョブカン                = 0
		株式会社システムシェアード  = 1
		萩原北都テクノ株式会社      = 2
		TDIシステムサービス         = 3
		トーテック                  = 4
		システムサポート            = 5
		CEC                        = 6


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
	戻り値 辞書リスト
        name 姓名　
        day datetime.date(yyyy,MM,dd) => yyyy-MM-dd
        worktime HH:mm
        starttime HH:mm　NULL OK
        endtime HH:mm　NULL OK
        resttime HH:mm　NULL OK
        note string　NULL OK
		
		companyFormatList = 
　　　{'name': '佐々木麻緒', 
　　　　'work_days': [
              {'day': '2024-05-01', 'worktime': '08:15', 'starttime': '08:45', 'endtime': '18:00', 'resttime': '01:00', 'note': ''}, 
              {'day': '2024-05-02', 'worktime': '08:15', 'starttime': '08:45', 'endtime': '18:00', 'resttime': '01:00', 'note': ''}, 
              {'day': '2024-05-03', 'worktime': '', 'starttime': '', 'endtime': '', 'resttime': '', 'note': ''},
              {'day': '2024-05-04', 'worktime': '', 'starttime': '', 'endtime': '', 'resttime': '', 'note': ''},
              {.....},
              {'day': '2024-05-31', 'worktime': '08:15', 'starttime': '08:45', 'endtime': '18:00', 'resttime': '01:00', 'note': ''}
             ]
　　　　}
	
ジョブカンデータの読み込み

比較

出力　excel or CSV

ReturnFormat/read_company_file処理まとめ
def read_company_file(file_path)
	■ 名前取得 (full_name)  
	佐々木麻緒

	■ テーブル抽出 (pure_df)
	     日付 勤怠区分     開始     終了   休憩時間   労働時間    時間外     深夜   法定休日 法定休日深夜 メモ
	0    5/1(水)   出勤  08:45  18:00  01:00  08:15  00:00  00:00  00:00  00:00   
	1    5/2(木)   出勤  08:45  18:00  01:00  08:15  00:00  00:00  00:00  00:00 
	・・・・・・・・・
	30  5/31(金)   出勤  08:45  18:00  01:00  08:15  00:00  00:00  00:00  00:00

	■ 第一フォーマットに変更 (pure_df → firstFormat_df)
	    日付   実働時間   開始時間   終了時間   休憩時間 備考
	0   2024-05-01  08:15  08:45  18:00  01:00
	1   2024-05-02  08:15  08:45  18:00  01:00
	・・・・・
	30  2024-05-31  08:15  08:45  18:00  01:00

	■ カラム名を英語に変更 (firstFormat_df → englishFormat_df)
	    day   worktime   starttime   endtime   resttime note
	0   2024-05-01  08:15  08:45  18:00  01:00
	1   2024-05-02  08:15  08:45  18:00  01:00
	・・・・・
	30  2024-05-31  08:15  08:45  18:00  01:00

	■ データフレームの辞書リスト形式に変換 (englishFormat_df → dict_list)
	[
	{'day': '2024-05-01', 'worktime': '08:15', 'starttime': '08:45', 'endtime': '18:00', 'resttime': '01:00', 'note': ''},
	{'day': '2024-05-02', 'worktime': '08:15', 'starttime': '08:45', 'endtime': '18:00', 'resttime': '01:00', 'note': ''},
	{・・・・・},
	{'day': '2024-05-31', 'worktime': '08:15', 'starttime': '08:45', 'endtime': '18:00', 'resttime': '01:00', 'note': ''}
	]

	■ 名前と勤怠データを合わせたフォーマット(word_data)に変換する (full_name, dict_list → work_data)
	{'name': '佐々木麻緒', 
　　　　'work_days': [
              {'day': '2024-05-01', 'worktime': '08:15', 'starttime': '08:45', 'endtime': '18:00', 'resttime': '01:00', 'note': ''}, 
              {'day': '2024-05-02', 'worktime': '08:15', 'starttime': '08:45', 'endtime': '18:00', 'resttime': '01:00', 'note': ''}, 
              {'day': '2024-05-03', 'worktime': '', 'starttime': '', 'endtime': '', 'resttime': '', 'note': ''},
              {'day': '2024-05-04', 'worktime': '', 'starttime': '', 'endtime': '', 'resttime': '', 'note': ''},
              {.....},
              {'day': '2024-05-31', 'worktime': '08:15', 'starttime': '08:45', 'endtime': '18:00', 'resttime': '01:00', 'note': ''}
             ]
　　　　}

	■work_dataを返す
	return work_data

ファイル構成
main .py
higuchi.py
higuti_sanityse.py
higuti_util.py
murase.py