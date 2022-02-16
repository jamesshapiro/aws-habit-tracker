//aws cloudfront create-invalidation --distribution-id E70XD704NPJDM --paths "/*"
//aws s3 cp --recursive build/ s3://cdkhabits-habitsweakerpotionscombucketdff06391-116yh481gtpp6
import logo from './logo.svg';
import './App.css';
import React from 'react'
import Habit from './components/Habit/Habit'

import { Amplify, Auth } from 'aws-amplify'
import { Authenticator } from '@aws-amplify/ui-react'
import '@aws-amplify/ui-react/styles.css'

import awsExports from './aws-exports'
Amplify.configure(awsExports)

class App extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      habits: [],
      isMounted: false
    }
  }

  getNewEntries = () => {
    var default_user = "display"
    var url =
      process.env.REACT_APP_GET_HABITS_URL + `?user=${default_user}`
    fetch(url, {
      method: 'GET',
    })
      .then((response) => response.json())
      .then((data) => {
        const habitItems = data.Items.map((item) => {
          return {
            habitName: item.SK1.S.slice(6),
            habitColor: item.COLOR.S,
            habitPriority: item.hasOwnProperty('PRIORITY') ? parseInt(item.PRIORITY.S) : 0
          }
        })
        habitItems.sort(
          (habit1, habit2) => habit2.habitPriority - habit1.habitPriority
        )
        var newState = { habits: [...habitItems], isMounted: true }
        this.setState(newState)
      })
  }

  getHabitGraphs = () => {
    return <div className="habit-graphs">
      {this.state.habits.map(habit => {
        return <Habit habitName={habit.habitName} habitColor={habit.habitColor} />
      })}
    </div>
  }

  componentDidMount() {
    this.getNewEntries()
  }

  render() {
    return (
      <div>
        <div className="App">
          <h1 className="habit-h1">Habit Tracker</h1>
          {/* <button onClick={signOut}>Sign out</button> */}
          {this.state.isMounted && this.getHabitGraphs()}
        </div>
        <Authenticator>
          {({ signOut, user }) => (<p>Hello World!</p>)}
        </Authenticator>
      </div>
    )
  }
}

export default App;
