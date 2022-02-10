import logo from './logo.svg';
import './App.css';
import React from 'react'
import Habit from './components/Habit/Habit'
import Github from './components/Github/Github'

class App extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      habits: [],
      isMounted: false
    }
  }
  getNewEntries = () => {
    var url =
      process.env.REACT_APP_GET_HABITS_URL
    fetch(url, {
      method: 'GET',
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data)
        const habitItems = data.Items.map((item) => {
          return {
            habitName: item.SK1.S.slice(6),
            habitColor: item.COLOR.S
          }
        })
        var newState = { habits: [...habitItems], isMounted: true }
        this.setState(newState)
      })
  }

  getHabitGraphs = () => {
    return this.state.habits.map(habit => {
      return <Habit habitName={habit.habitName} habitColor={habit.habitColor} />
    })
  }

  componentDidMount() {
    this.getNewEntries()
  }

  render() {
    return (
      <div className="App">
        <h1 className="habit-title">Habit Tracker</h1>
        <Github />
        {this.state.isMounted && this.getHabitGraphs()}
      </div>
    )
  }
}

export default App;
