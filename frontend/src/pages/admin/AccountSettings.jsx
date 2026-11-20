import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import {
  updateAdminProfile,
  updateAdminPassword,
} from '../../services/authService'

function AccountSettings() {
  const { admin, updateAdmin } = useAuth()
  const navigate = useNavigate()

  const [profile, setProfile] = useState({
    username: admin?.username || '',
    email: admin?.email || '',
    currentPassword: '',
  })

  const [password, setPassword] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  })

  const [profileError, setProfileError] = useState('')
  const [profileSuccess, setProfileSuccess] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [passwordSuccess, setPasswordSuccess] = useState('')
  const [savingProfile, setSavingProfile] = useState(false)
  const [savingPassword, setSavingPassword] = useState(false)

  function handleProfileChange(event) {
    const { name, value } = event.target

    setProfile((current) => ({
      ...current,
      [name]: value,
    }))
  }

  function handlePasswordChange(event) {
    const { name, value } = event.target

    setPassword((current) => ({
      ...current,
      [name]: value,
    }))
  }

  async function handleProfileSubmit(event) {
    event.preventDefault()
    setProfileError('')
    setProfileSuccess('')
    setSavingProfile(true)

    try {
      const updatedAdmin = await updateAdminProfile({
        username: profile.username.trim(),
        email: profile.email.trim(),
        current_password: profile.currentPassword,
      })

      updateAdmin(updatedAdmin)

      setProfile((current) => ({
        ...current,
        currentPassword: '',
      }))

      setProfileSuccess('Your account details have been updated.')
    } catch (error) {
      setProfileError(error.message || 'Could not update your profile.')
    } finally {
      setSavingProfile(false)
    }
  }

  async function handlePasswordSubmit(event) {
    event.preventDefault()
    setPasswordError('')
    setPasswordSuccess('')

    if (password.newPassword.length < 12) {
      setPasswordError('Your new password must contain at least 12 characters.')
      return
    }

    if (password.newPassword !== password.confirmPassword) {
      setPasswordError('Your new passwords do not match.')
      return
    }

    setSavingPassword(true)

    try {
      await updateAdminPassword({
        current_password: password.currentPassword,
        new_password: password.newPassword,
      })

      updateAdmin(null)

      navigate('/admin/login', {
        replace: true,
        state: {
          message: 'Password updated successfully. Please sign in with your new password.',
        },
      })
    } catch (error) {
      setPasswordError(error.message || 'Could not update your password.')
    } finally {
      setSavingPassword(false)
    }
  }

  return (
    <section className="admin-account-page">
      <div className="admin-page-heading">
        <h2>Account Settings</h2>
        <p>Manage your administrator profile and password.</p>
      </div>

      <article className="admin-account-card">
        <div className="admin-account-card-heading">
          <h3>Profile Information</h3>
          <p>Update the username and email address used for your admin account.</p>
        </div>

        <form onSubmit={handleProfileSubmit} className="admin-account-form">
          <label htmlFor="account-username">Username</label>
          <input
            id="account-username"
            name="username"
            type="text"
            value={profile.username}
            onChange={handleProfileChange}
            minLength={2}
            maxLength={80}
            autoComplete="username"
            required
          />

          <label htmlFor="account-email">Email address</label>
          <input
            id="account-email"
            name="email"
            type="email"
            value={profile.email}
            onChange={handleProfileChange}
            maxLength={120}
            autoComplete="email"
            required
          />

          <label htmlFor="profile-current-password">
            Confirm with current password
          </label>
          <input
            id="profile-current-password"
            name="currentPassword"
            type="password"
            value={profile.currentPassword}
            onChange={handleProfileChange}
            autoComplete="current-password"
            required
          />

          {profileError && (
            <p className="admin-error" role="alert">
              {profileError}
            </p>
          )}

          {profileSuccess && (
            <p className="admin-success" role="status">
              {profileSuccess}
            </p>
          )}

          <button
            type="submit"
            className="admin-primary-button"
            disabled={savingProfile}
          >
            {savingProfile ? 'Saving...' : 'Save Profile'}
          </button>
        </form>
      </article>

      <article className="admin-account-card">
        <div className="admin-account-card-heading">
          <h3>Change Password</h3>
          <p>
            Use at least 12 characters. Changing your password signs out
            all existing administrator sessions.
          </p>
        </div>

        <form onSubmit={handlePasswordSubmit} className="admin-account-form">
          <label htmlFor="password-current">Current password</label>
          <input
            id="password-current"
            name="currentPassword"
            type="password"
            value={password.currentPassword}
            onChange={handlePasswordChange}
            autoComplete="current-password"
            required
          />

          <label htmlFor="password-new">New password</label>
          <input
            id="password-new"
            name="newPassword"
            type="password"
            value={password.newPassword}
            onChange={handlePasswordChange}
            minLength={12}
            maxLength={128}
            autoComplete="new-password"
            required
          />

          <label htmlFor="password-confirm">Confirm new password</label>
          <input
            id="password-confirm"
            name="confirmPassword"
            type="password"
            value={password.confirmPassword}
            onChange={handlePasswordChange}
            minLength={12}
            maxLength={128}
            autoComplete="new-password"
            required
          />

          {passwordError && (
            <p className="admin-error" role="alert">
              {passwordError}
            </p>
          )}

          {passwordSuccess && (
            <p className="admin-success" role="status">
              {passwordSuccess}
            </p>
          )}

          <button
            type="submit"
            className="admin-primary-button"
            disabled={savingPassword}
          >
            {savingPassword ? 'Updating...' : 'Update Password'}
          </button>
        </form>
      </article>
    </section>
  )
}

export default AccountSettings
