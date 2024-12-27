import React, { useEffect, useState } from 'react';
import axios from 'axios';

function DifferenceList() {
  // ステートを作成
  const [differences, setDifferences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filteredDifferences, setFilteredDifferences] = useState([]);
  const [filter, setFilter] = useState({ yearMonth: '', name: '' });

  // APIを呼び出してデータを取得
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/false-data');
        // yearMonth を基準に降順（新しい順）でデータを並べ替え。
        const sortedDifferences = response.data.differences.sort((a, b) =>
          b.yearMonth.localeCompare(a.yearMonth)
        );
        setDifferences(sortedDifferences);
        setFilteredDifferences(sortedDifferences); // 初期値
      } catch (error) {
        console.error('データの取得中にエラーが発生しました:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // フィルタリング処理
  useEffect(() => {
    const filtered = differences.filter((diff) => {
      const matchesYearMonth =
        !filter.yearMonth || diff.yearMonth.includes(filter.yearMonth);
      const matchesName = !filter.name || diff.name.includes(filter.name);
      return matchesYearMonth && matchesName;
    });
    setFilteredDifferences(filtered);
  }, [filter, differences]);

  // ローディング中の表示
  if (loading) {
    return <p className="loading-message">データを読み込み中...</p>;
  }

  return (
    <main>
      <h2>差異一覧</h2>

      {/* フィルタリングフォーム */}
      <div className="filter-form">
        <label>
          年月:
          <input
            type="text"
            value={filter.yearMonth}
            onChange={(e) =>
              setFilter((prev) => ({ ...prev, yearMonth: e.target.value }))
            }
          />
        </label>
        <label>
          従業員名:
          <input
            type="text"
            value={filter.name}
            onChange={(e) =>
              setFilter((prev) => ({ ...prev, name: e.target.value }))
            }
          />
        </label>
      </div>

      {/* データの表示 */}
      {filteredDifferences.length === 0 ? (
        <p className="no-results">条件に一致する差異データがありません。</p>
      ) : (
        filteredDifferences.map((diff, index) => (
          <div
            key={index}
            className="difference-item"
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