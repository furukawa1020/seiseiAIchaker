'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { MessageSquare } from 'lucide-react'
import { workApi } from '@/lib/api'

interface ClaimCardFormProps {
  workId: string
  onSuccess?: () => void
}

interface FormData {
  claim_text: string
  context: string
  page_numbers: string
}

export function ClaimCardForm({ workId, onSuccess }: ClaimCardFormProps) {
  const [submitting, setSubmitting] = useState(false)
  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormData>()

  const onSubmit = async (data: FormData) => {
    try {
      setSubmitting(true)
      await workApi.createCard(workId, {
        claim_text: data.claim_text,
        context: data.context,
        page_numbers: data.page_numbers || undefined,
      })
      reset()
      onSuccess?.()
    } catch (error) {
      console.error('Failed to create card:', error)
      alert('カードの作成に失敗しました')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          主張・引用テキスト <span className="text-red-500">*</span>
        </label>
        <textarea
          {...register('claim_text', { required: '主張は必須です' })}
          className="textarea"
          placeholder="例: 深層学習は画像認識において人間を超える精度を達成した"
          rows={3}
        />
        {errors.claim_text && (
          <p className="text-red-600 text-sm mt-1">{errors.claim_text.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          文脈・コメント <span className="text-red-500">*</span>
        </label>
        <textarea
          {...register('context', { required: '文脈は必須です' })}
          className="textarea"
          placeholder="例: ImageNetベンチマークにおいて、2015年にResNetがエラー率3.57%を達成"
          rows={3}
        />
        {errors.context && (
          <p className="text-red-600 text-sm mt-1">{errors.context.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          ページ番号 (任意)
        </label>
        <input
          {...register('page_numbers')}
          type="text"
          className="input"
          placeholder="例: 5-7, 12"
        />
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="btn btn-primary w-full"
      >
        {submitting ? '作成中...' : '📝 カードを作成'}
      </button>
    </form>
  )
}
