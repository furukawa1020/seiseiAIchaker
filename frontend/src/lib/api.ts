import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Work {
  id: string
  type: string
  title: string
  doi?: string
  url?: string
  issued_year?: number
  container_title?: string
  authors?: Array<{ family: string; given?: string }>
  peer_reviewed?: number
  retracted?: number
  consensus_score?: number
  citation_count?: number
}

export interface Check {
  id: string
  work_id: string
  check_type: string
  status: 'success' | 'warning' | 'error'
  message: string
  checked_at: string
}

export interface ClaimCard {
  id: string
  work_id: string
  claim_text: string
  context: string
  page_numbers?: string
  created_at: string
}

export const workApi = {
  // Works
  async getWorks(limit?: number): Promise<Work[]> {
    const params = limit ? { limit } : {}
    const { data } = await api.get('/api/works', { params })
    return data
  },

  async getWork(id: string): Promise<Work> {
    const { data } = await api.get(`/api/works/${id}`)
    return data
  },

  async uploadPdf(file: File): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)
    
    const { data } = await api.post('/api/works/upload-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return data
  },

  async importWorks(cslJson: any): Promise<any> {
    const { data } = await api.post('/api/works/import', cslJson)
    return data
  },

  async verifyWork(id: string): Promise<any> {
    const { data } = await api.post(`/api/works/${id}/verify`)
    return data
  },

  async getCitation(id: string, format: string = 'apa'): Promise<string> {
    const { data } = await api.get(`/api/works/${id}/cite`, {
      params: { format },
    })
    return data.citation
  },

  // Checks
  async getChecks(workId: string): Promise<Check[]> {
    const { data } = await api.get(`/api/works/${workId}/checks`)
    return data
  },

  // Cards
  async getCards(workId: string): Promise<ClaimCard[]> {
    const { data } = await api.get(`/api/works/${workId}/cards`)
    return data
  },

  async createCard(workId: string, card: {
    claim_text: string
    context: string
    page_numbers?: string
  }): Promise<ClaimCard> {
    const { data } = await api.post(`/api/works/${workId}/cards`, card)
    return data
  },

  // Reading Evidence
  async getReadingScore(workId: string): Promise<any> {
    const { data } = await api.get(`/api/works/${workId}/reading-score`)
    return data
  },

  async submitReadingEvidence(workId: string, evidence: {
    page_numbers: string
    notes?: string
  }): Promise<any> {
    const { data } = await api.post(`/api/works/${workId}/reading-evidence`, evidence)
    return data
  },

  // Export
  async exportBibliography(workIds: string[], format: string = 'apa'): Promise<string> {
    const { data } = await api.post('/api/export/bibliography', {
      work_ids: workIds,
      format,
    })
    return data.bibliography
  },
}
