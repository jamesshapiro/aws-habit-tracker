//aws cloudfront create-invalidation --distribution-id E70XD704NPJDM --paths "/*"
//aws s3 cp --recursive build/ s3://cdkhabits-habitsweakerpotionscombucketdff06391-116yh481gtpp6
import './App.css';
import React from 'react'
import Habit from './components/Habit/Habit'

import { Amplify, Auth } from 'aws-amplify'
import { Authenticator } from '@aws-amplify/ui-react'
import '@aws-amplify/ui-react/styles.css'

import awsExports from './aws-exports'
Amplify.configure(awsExports)

async function signOut() {
  try {
    await Auth.signOut()
    window.location.reload(false)
  } catch (error) {
    console.log('error signing out: ', error)
  }
}

class App extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      habits: [],
      isMounted: false,
      isLoginPage: false,
      isInEditHabitsMode: false,
    }
  }

  enterEditHabitsMode = () => {
    this.setState({ isInEditHabitsMode: true })
  }

  exitEditHabitsMode = () => {
    this.setState({ isInEditHabitsMode: false })
  }

  getNewEntries = () => {
    Auth.currentAuthenticatedUser()
      .then((user) => {
        const username = user.attributes.email.replace('@', '%40')
        const token = user.signInUserSession.idToken.jwtToken
        const headers = {
          'Content-Type': 'application/json',
          Authorization: token,
        }
        var url =
          process.env.REACT_APP_GET_HABITS_AUTH_URL + `?user=${username}`
        fetch(url, {
          method: 'GET',
          headers: headers,
        })
          .then((response) => response.json())
          .then((data) => {
            const habitItems = data.Items.map((item) => {
              return {
                habitName: item.SK1.S.slice(6),
                habitColor: item.COLOR.S,
                habitPriority: item.hasOwnProperty('PRIORITY')
                  ? parseInt(item.PRIORITY.S)
                  : 0,
              }
            })
            habitItems.sort(
              (habit1, habit2) => habit2.habitPriority - habit1.habitPriority
            )
            var newState = {
              habits: [...habitItems],
              isMounted: true,
              isLoginPage: false,
            }
            this.setState(newState)
          })
      })
      .catch((err) => {
        const habits = [
          {
            habitName: 'clean-for-10m',
            habitColor: '#b92514',
            habitPriority: 100,
          },
          {
            habitName: 'get-8h-of-sleep',
            habitColor: '#2270A1',
            habitPriority: 99,
          },
          {
            habitName: 'stay-hydrated',
            habitColor: '#1e4500',
            habitPriority: 98,
          },
          {
            habitName: 'read-for-30m',
            habitColor: '#b92514',
            habitPriority: 97,
          },
          {
            habitName: 'exercise',
            habitColor: '#2270A1',
            habitPriority: 96,
          },
        ]
        var newState = {
          habits: habits,
          isMounted: true,
          isLoginPage: false,
        }
        this.setState(newState)
        return
      })
  }

  getHabitGraphs = () => {
    return (
      <div className="habit-graphs">
        {this.state.habits.map((habit) => {
          return (
            <Habit habitName={habit.habitName} habitColor={habit.habitColor} />
          )
        })}
      </div>
    )
  }

  getEditHabitsUI = () => {
    console.log(this.state.habits)
    return (
      <div className="habit-graphs">
        {this.state.habits.map((habit) => {
          return (
            // <Habit habitName={habit.habitName} habitColor={habit.habitColor} />
            <li>{habit.habitName}</li>
          )
        })}
      </div>
    )
  }

  componentDidMount() {
    this.getNewEntries()
  }

  goToLogin = () => {
    let newState = {
      isLoginPage: true,
    }
    this.setState(newState)
  }

  getIsLoggedIn = () => {
    let userIsLoggedIn = false
    Object.keys(localStorage).map((key) => {
      if (
        key.startsWith('CognitoIdentityServiceProvider') &&
        key.endsWith('LastAuthUser')
      ) {
        userIsLoggedIn = true
      }
    })
    return userIsLoggedIn
  }

  getGraphsForUser = () => {
    return (
      <div>
        <div className="App">
          <div className="habit-h1">
            {!this.state.isInEditHabitsMode && 'Habit Tracker'}
            {!this.getIsLoggedIn() && (
              <button onClick={this.goToLogin}>Login/Signup</button>
            )}
            {this.getIsLoggedIn() && (
              <button onClick={() => signOut()}>Signout</button>
            )}
            {this.getIsLoggedIn() && !this.state.isInEditHabitsMode && (
              <button onClick={() => this.enterEditHabitsMode()}>
                Edit Habits
              </button>
            )}
            {this.getIsLoggedIn() && this.state.isInEditHabitsMode && (
              <button onClick={() => this.exitEditHabitsMode()}>
                Back to Grid!
              </button>
            )}
          </div>
          <h1 className="habit-h1">{}</h1>
          {this.state.isMounted &&
            !this.state.isInEditHabitsMode &&
            this.getHabitGraphs()
          }
          {this.state.isMounted &&
            this.state.isInEditHabitsMode &&
            this.getEditHabitsUI()
          }
        </div>
      </div>
    )
  }

  getFrontPage = () => {
    if (this.state.isLoginPage) {
      return (
        <Authenticator>
          {() => {
            this.setState({ isLoginPage: false })
            window.location.reload(false)
            return this.getGraphsForUser()
          }}
        </Authenticator>
      )
    } else {
      return this.getGraphsForUser()
    }
  }

  render() {
    return this.getFrontPage()
  }
}

export default App;
