import React, { useEffect, useState } from 'react';
import axios from 'axios';

function DifferenceList() {
  // ステートを作成
  const [differences, setDifferences] = useState([]);
  const [loading, setLoading] = useState(true);

  // APIを呼び出してデータを取得
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/false-data');
        setDifferences(response.data.differences);
      } catch (error) {
        console.error('データの取得中にエラーが発生しました:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // ローディング中の表示
  if (loading) {
    return <p>データを読み込み中...</p>;
  }

  return (
    <main>
      <h2>差異一覧</h2>
      {differences.length === 0 ? (
        <p>差異データがありません。</p>
      ) : (
        differences.map((diff, index) => (
          <div
            key={index}
            style={{ border: '1px solid #ddd', padding: '10px', marginBottom: '10px' }}
          >
            <h3>{diff.yearMonth}</h3>
            <p>ファイル名: {diff.fileName}</p>
            <p>従業員名: {diff.name}</p>
            <p>差異日: {diff.dates}</p>
          </div>
        ))
      )}
    </main>
  );
}

export default DifferenceList;