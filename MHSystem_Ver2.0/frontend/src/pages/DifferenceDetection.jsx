import React, { useState } from 'react';
import axios from 'axios';

function DifferenceDetection() {
  const [yearMonth, setYearMonth] = useState('');
  const [result, setResult] = useState('');
  const [isProcessing, setIsProcessing] = useState(false); // 処理中かどうかの状態

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsProcessing(true); // ボタンを非活性化
    setResult('差異検出中...'); // 処理中の表示
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/detect', {
        yearMonth: yearMonth,
      });
      console.log("接続に成功しました！");
      setResult(response.data.differences.join(', '));
    } catch (error) {
      console.error("APIエラー:", error);
      setResult('差異検出中にエラーが発生しました');
    } finally {
      setIsProcessing(false); // 処理が終わったらボタンを有効化
    }
  };

  return (
    <main>
      <h2>差異検出</h2>
      <form onSubmit={handleSubmit}>
        <label htmlFor="yearMonth">対象年月:</label>
        <input
          type="month"
          id="yearMonth"
          value={yearMonth}
          onChange={(e) => setYearMonth(e.target.value)}
        />
      </form>
      <div className="textarea-wrapper">
        <button
          type="submit"
          className="detect-button"
          onClick={handleSubmit}
          disabled={isProcessing} // 処理中はボタンを非活性化
        >
          差異を検出
        </button>
        <textarea
          readOnly
          value={result || "結果がここに表示されます"}
          className="result-textarea"
        />
      </div>
    </main>
  );
}

export default DifferenceDetection;