import logo from './logo.svg';
import './App.css';
import React from 'react'
import Habit from './components/Habit/Habit'

class App extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      dataPoints: [],
    }
  }
  getNewEntries = () => {
    var url = process.env.REACT_APP_URL + '?PK1=read-a-book-for-10m'
    fetch(url, {
      method: 'GET',
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data)
        var newState = { dataPoints: [...data.Items] }
        this.setState(newState)
      })
  }

  componentDidMount() {
    this.getNewEntries()
  }

  render() {
    return (
      <div className="App">
        <h1 className="habit-title">Habit Tracker</h1>
        <Habit habitName="Go to sleep before midnight" />
        <Habit habitName="Read for 15m+" />
      </div>
    )
  }
}

export default App;
