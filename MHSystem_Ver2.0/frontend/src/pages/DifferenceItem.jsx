import React from 'react';

function DifferenceItem({ yearMonth, fileName, name, dates }) {
  return (
    <div style={{ border: '1px solid #ddd', padding: '10px', marginBottom: '10px' }}>
      <h3>{yearMonth}</h3>
      <p>ファイル名: {fileName}</p>
      <p>従業員名: {name}</p>
      <p>差異日: {dates.join(', ')}</p>
    </div>
  );
}

export default DifferenceItem;