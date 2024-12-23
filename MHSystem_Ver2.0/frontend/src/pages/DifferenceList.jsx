import React from 'react';
import DifferenceItem from './DifferenceItem';

function DifferenceList() {
  const differences = [
    // {
    //   yearMonth: '2024年11月',
    //   fileName: 'トーテック勤怠表.pdf',
    //   name: '佐々木',
    //   dates: ['11/02', '11/03', '11/04'],
    // },
    // {
    //   yearMonth: '2024年10月',
    //   fileName: '勤怠表.pdf',
    //   name: '佐藤',
    //   dates: ['10/12', '10/13', '10/14'],
    // },
    // {
    //   yearMonth: '2024年9月',
    //   fileName: '勤怠表.pdf',
    //   name: '佐藤',
    //   dates: ['9/12', '9/13', '9/14'],
    // },
    // {
    //   yearMonth: '2024年8月',
    //   fileName: '勤怠表.pdf',
    //   name: '佐藤',
    //   dates: ['8/12', '8/13', '8/14'],
    // },
  ];
  
  return (
    <main>
      <h2>差異一覧</h2>
      {differences.map((diff, index) => (
        <DifferenceItem key={index} {...diff} />
      ))}
    </main>
  );
}

export default DifferenceList;