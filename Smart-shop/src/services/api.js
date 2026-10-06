import axios from 'axios'

/**
 * Axios instance (API-ready)
 * Update baseURL when backend is available.
 */
export const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
})

