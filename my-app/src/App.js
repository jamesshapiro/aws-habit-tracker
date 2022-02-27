/////////////////PROD//////////////////
// npm run build
// PROD: aws s3 cp --recursive build/ s3://cdkhabits-githabitcombucket6a79c338-hk3nkues0h5f
// PROD: aws cloudfront create-invalidation --distribution-id E2WZ67Q81CV1B5 --paths "/*"
// FFB: npm run build && aws s3 cp --recursive build/ s3://cdkhabits-githabitcombucket6a79c338-hk3nkues0h5f && aws cloudfront create-invalidation --distribution-id E2WZ67Q81CV1B5 --paths "/*"
/////////////////PROD//////////////////
// npm run build
// DEV: aws s3 cp --recursive build/ s3://cdkhabits-habitsweakerpotionscombucketdff06391-116yh481gtpp6
// DEV: aws cloudfront create-invalidation --distribution-id E70XD704NPJDM --paths "/*"
import './App.css'
import React from 'react'
import Habit from './components/Habit/Habit'
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useHistory
} from 'react-router-dom'

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
      newHabit: '',
    }
  }

  handleChange(i, event) {
    let habits = [...this.state.habits]
    habits[i] = event.target.value
    this.setState({ newHabit: event.target.value })
  }

  get_pk1_habit_name(habitName) {
    return habitName.toLowerCase().split(/\s+/).join('-')
  }

  getTodayDateString() {
    const today = new Date()
    const dd = String(today.getDate()).padStart(2, '0')
    const mm = String(today.getMonth() + 1).padStart(2, '0')
    const yyyy = today.getFullYear()
    return `${yyyy}-${mm}-${dd}`
  }

  addClick = () => {
    let habits = [...this.state.habits]
    let newHabit = this.state.newHabit
    habits.push({
      habitName: this.get_pk1_habit_name(newHabit),
      habitDisplayName: newHabit,
      habitColor: '#b92514',
      habitPriority: 0,
      habitCreationDate: this.getTodayDateString()
    })
    if (newHabit.length > 2) {
      this.setState({ newHabit: '', habits })
      this.handleSubmit(habits.length - 1)
    }
  }

  unremoveClick(i) {
    let values = [...this.state.habits]
    values[i].deletePlanned = false
    this.setState({ habits: values })
    this.handleSubmit(i)
  }

  removeClick(i) {
    console.log('calling removeClick')
    let values = [...this.state.habits]
    values[i].deletePlanned = true
    this.setState({ habits: values })
    this.handleSubmit(i)
  }

  handleSubmit = (i) => {
    console.log('handling submit')
    Auth.currentAuthenticatedUser()
      .then((user) => {
        const token = user.signInUserSession.idToken.jwtToken
        const headers = {
          'Content-Type': 'application/json',
          Authorization: token,
        }
        const url = process.env.REACT_APP_GET_HABITS_AUTH_URL
        const data = [this.state.habits[i]]
        fetch(url, {
          method: 'POST',
          headers: headers,
          body: JSON.stringify(data),
        }).then((response) => {
          this.setState({
            showEntries: true,
            values: [''],
          })
        })
      })
      .catch((err) => {
        console.log(err)
      })
  }

  createUI = () => {
    return (
      <>
        <table className="habit-ui-table">
          <tbody>
            {this.state.habits.map((el, i) => (
              <tr className="tr-existing-habit" key={i}>
                <td className="td-existing-habit">
                  <div className="div-existing-habit">
                    {el.deletePlanned ? (
                      <span className="to-delete">{el.habitDisplayName}</span>
                    ) : (
                      el.habitDisplayName
                    )}
                  </div>
                </td>
                <td className="td-button">
                  {el.deletePlanned ? (
                    <div>
                      <span type="button" className="to-delete-button">
                        💀
                      </span>
                      <span
                        type="button"
                        className="bullet-button"
                        onClick={this.unremoveClick.bind(this, i)}
                      >
                        ➕
                      </span>
                    </div>
                  ) : (
                    <div
                      type="button"
                      className="bullet-button"
                      onClick={this.removeClick.bind(this, i)}
                    >
                      ❌
                    </div>
                  )}
                </td>
              </tr>
            ))}
            <tr key={this.state.habits.length}>
              <td className="td-textarea">
                <input
                  placeholder={'Ex. "Get 8+ hours of sleep"'}
                  className="bullet-textarea"
                  onChange={this.handleChange.bind(
                    this,
                    this.state.habits.length
                  )}
                />
              </td>
              <td className="td-button">
                <div
                  type="button"
                  className="bullet-button"
                  onClick={this.addClick.bind(this)}
                >
                  ➕
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        {/* <span
          className="back-to-grid-body"
        >
          Back to Grid!
        </span> */}
      </>
    )
  }

  getNewEntries = () => {
    Auth.currentAuthenticatedUser()
      .then((user) => {
        const token = user.signInUserSession.idToken.jwtToken
        const headers = {
          'Content-Type': 'application/json',
          Authorization: token,
        }
        const url = process.env.REACT_APP_GET_HABITS_AUTH_URL
        fetch(url, {
          method: 'GET',
          headers: headers,
        })
          .then((response) => response.json())
          .then((data) => {
            const habitItems = data.map((item) => {
              return {
                habitDisplayName: item.DISPLAY_NAME.S,
                habitName: item.SK1.S.slice(6),
                habitColor: item.COLOR.S,
                habitPriority: parseInt(item.PRIORITY.S),
                habitCreationDate: item.CREATION_DATE.S
              }
            })
            const newState = {
              habits: [...habitItems],
              isMounted: true,
            }
            this.setState(newState)
          })
      })
      .catch((err) => {
        const habits = [
          {
            habitName: 'clean-for-10m',
            habitDisplayName: 'Clean for 10m',
            habitColor: '#b92514',
            habitPriority: 100,
            habitCreationDate: '2000-01-01'
          },
          {
            habitName: 'get-8h-of-sleep',
            habitDisplayName: 'Get 8h of sleep',
            habitColor: '#2270A1',
            habitPriority: 99,
            habitCreationDate: '2000-01-01'
          },
          {
            habitName: 'stay-hydrated',
            habitDisplayName: 'Stay Hydrated',
            habitColor: '#1e4500',
            habitPriority: 98,
            habitCreationDate: '2000-01-01'
          },
          {
            habitName: 'read-for-30m',
            habitDisplayName: 'Read for 30m',
            habitColor: '#b92514',
            habitPriority: 97,
            habitCreationDate: '2000-01-01'
          },
          {
            habitName: 'exercise',
            habitDisplayName: 'Exercise',
            habitColor: '#2270A1',
            habitPriority: 96,
            habitCreationDate: '2000-01-01'
          },
        ]
        var newState = {
          habits: habits,
          isMounted: true,
        }
        this.setState(newState)
        return
      })
  }

  habitsContainGithub = () => {
    let result = false
    for (let i = 0; i < this.state.habits.length; i++) {
      if (this.state.habits[i].habitName.toLowerCase().includes('github')) {
        return true
      }
    }
    return false
  }

  getHabitGraphs = () => {
    return (
      <div className="habit-graphs">
        {this.state.habits.map((habit, i) => {
          return <Habit habit={habit} key={i} idx={i} startIdx={this.habitsContainGithub() ? 1 : 0} />
        })}
      </div>
    )
  }

  getEditHabitsUI = () => {
    return this.createUI()
  }

  componentDidMount() {
    this.getNewEntries()
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

  getEditHabitsMode = () => {
    return (
      <div>
        <div className="App">
          <div className="nav-bar-div">
            <span className="left-elem">
              <span className="nav-bar-cell habit-tracker-header">
                Edit Habits
              </span>
            </span>
            <span className="right-elem">
              <span
                className="nav-bar-cell clickable"
                id="login-logout-button"
                onClick={() => signOut()}
              >
                <Link to="/">Signout</Link>
              </span>
            </span>
            <span className="right-elem">
              <span className="nav-bar-cell clickable" id="login-logout-button">
                <Link to="/">Back to Grid!</Link>
              </span>
            </span>
          </div>
          <span className="demo-user">🐇 Keep it up! 🥕</span>
          {this.state.isMounted && this.getEditHabitsUI()}
        </div>
        <div className="blank-footer" />
      </div>
    ) 
  }

  getMainEditHabitsView = () => {
    return !this.getIsLoggedIn()
      ? this.getLoggedOutMode()
      : this.getEditHabitsMode()
  }

  getLoggedOutMode = () => {
    return (
      <div>
        <div className="App">
          <div className="nav-bar-div">
            <span className="left-elem">
              <span className="nav-bar-cell habit-tracker-header">
                Habit Tracker
              </span>
            </span>
            <span className="right-elem">
              <span className="nav-bar-cell clickable" id="login-logout-button">
                <Link to="/login">Login/Signup</Link>
              </span>
            </span>
          </div>
          <div className="demo-user-div">
            <span className="demo-user">Roger Habit</span>
          </div>
          {this.state.isMounted && this.getHabitGraphs()}
        </div>
        <div className="blank-footer" />
      </div>
    )
  }

  getLoggedInMode = () => {
    return (
      <>
        <div className="App">
          <div className="nav-bar-div">
            <span className="left-elem">
              <span className="nav-bar-cell habit-tracker-header">
                Habit Tracker
              </span>
            </span>
            <span className="right-elem">
              <span
                className="nav-bar-cell clickable"
                id="login-logout-button"
                onClick={() => signOut()}
              >
                <Link to="/">Signout</Link>
              </span>
            </span>
            <span className="right-elem">
              <span className="nav-bar-cell clickable" id="login-logout-button">
                <Link to="/edit-habits">Edit Habits</Link>
              </span>
            </span>
          </div>
          <div className="demo-user-div">
            <span className="demo-user">🐇 Keep it up! 🥕</span>
          </div>
          {this.state.isMounted && this.getHabitGraphs()}
        </div>
        <div className="blank-footer" />
      </>
    )
  }

  getMainView = () => {
    return !this.getIsLoggedIn()
      ? this.getLoggedOutMode()
      : this.getLoggedInMode()
  }
  render() {
    const validPaths = ['', '/login', '/edit-habits']
    validPaths.forEach((item) =>
      validPaths.push(item + '/')
    )
    if (
      window.location.pathname &&
      !validPaths.includes(window.location.pathname)
    ) {
      // console.log(`window.location.path == ${window.location.pathname}`)
      window.location = 'https://githabit.com'
    }
    if (
      window.location.pathname && !this.getIsLoggedIn() && !['', '/', '/login', '/login/'].includes(window.location.pathname)
    ) {
      // console.log(`window.location.path == ${window.location.pathname}`)
      window.location = 'https://githabit.com'
    }
    return (
      <Router>
        <Switch>
          <Route path="/login">
            <Authenticator>
              {() => {
                const history = useHistory()
                history.push('/')
                window.location.reload(false)
                return this.getMainView()
              }}
            </Authenticator>
          </Route>
          <Route path="/edit-habits">{this.getMainEditHabitsView()}</Route>
          <Route path="/">{this.getMainView()}</Route>
        </Switch>
      </Router>
    )
  }
}

export default App
