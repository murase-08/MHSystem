import React from 'react';
import { NavLink } from 'react-router-dom';

function Navigation() {
  return (
    <nav>
      <NavLink to="/" className="nav-item" activeClassName="active">
        差異検出
      </NavLink>
      <NavLink to="/difference-list" className="nav-item hidden" activeClassName="active">
        差異一覧
      </NavLink>
      <a href="#" className="nav-item hidden">未定</a>
      <a href="#" className="nav-item hidden">未定</a>
    </nav>
  );
}

export default Navigation;