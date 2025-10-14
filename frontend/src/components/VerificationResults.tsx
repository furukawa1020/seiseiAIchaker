import { CheckCircle, AlertTriangle, XCircle, Clock } from 'lucide-react'
import { Check } from '@/lib/api'
import { formatDate } from '@/lib/utils'

interface VerificationResultsProps {
  checks: Check[]
}

export function VerificationResults({ checks }: VerificationResultsProps) {
  if (checks.length === 0) {
    return null
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />
      default:
        return <Clock className="w-5 h-5 text-gray-600" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return 'badge-success'
      case 'warning':
        return 'badge-warning'
      case 'error':
        return 'badge-danger'
      default:
        return 'badge-info'
    }
  }

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-6">
        <CheckCircle className="w-6 h-6 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-900">検証結果</h2>
        <span className="badge badge-info">{checks.length}件</span>
      </div>

      <div className="space-y-3">
        {checks.map((check) => (
          <div
            key={check.id}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                {getStatusIcon(check.status)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`badge ${getStatusBadge(check.status)}`}>
                    {check.check_type}
                  </span>
                  <span className="text-xs text-gray-500">
                    {formatDate(check.checked_at)}
                  </span>
                </div>
                
                <p className="text-sm text-gray-700 break-words">
                  {check.message}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
