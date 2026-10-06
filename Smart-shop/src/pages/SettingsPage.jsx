import { useState } from 'react'
import { Button } from '../components/ui/Button.jsx'
import { Input } from '../components/ui/Input.jsx'
import { useAuth } from '../context/AuthContext.jsx'

export function SettingsPage() {
  const { user } = useAuth()
  const [orgName, setOrgName] = useState('Demo Retail Store')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const onSave = async (e) => {
    e.preventDefault()
    setSaved(false)
    setSaving(true)
    await new Promise((r) => setTimeout(r, 700))
    setSaving(false)
    setSaved(true)
  }

  return (
    <div className="space-y-4">
      <div className="card p-6">
        <div className="text-lg font-semibold text-white">Settings</div>
        <div className="mt-1 text-sm text-slate-400">
          Configure your workspace. These settings are mocked for now.
        </div>
      </div>

      <div className="card p-6">
        <form onSubmit={onSave} className="space-y-4">
          <Input
            id="org"
            label="Organization / Store name"
            value={orgName}
            onChange={(e) => setOrgName(e.target.value)}
          />

          <Input id="email" label="Account email" value={user?.email || ''} disabled />

          <div className="flex items-center gap-3">
            <Button type="submit" isLoading={saving}>
              Save changes
            </Button>
            {saved ? <div className="text-sm text-emerald-300">Saved</div> : null}
          </div>
        </form>
      </div>
    </div>
  )
}

