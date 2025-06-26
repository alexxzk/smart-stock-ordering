import { useState } from 'react'
import { Upload, FileText, AlertCircle, CheckCircle, Loader, Database, FileSpreadsheet } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useAppState } from '../contexts/AppStateContext'
import { ApiService } from '../services/apiService'

interface CSVUploadProps {
  onDataProcessed?: (data: { headers: string[], rows: string[][], preview: string[][] }) => void
  onError?: (error: string) => void
}

interface ProcessingStep {
  name: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  progress: number
  message: string
}

export default function CSVUpload({ onDataProcessed, onError }: CSVUploadProps) {
  const { currentUser } = useAuth()
  const { addUploadedFile } = useAppState()
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [processedData, setProcessedData] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [processingSteps, setProcessingSteps] = useState<ProcessingStep[]>([
    { name: 'Reading CSV File', status: 'pending', progress: 0, message: 'Waiting to start...' },
    { name: 'Parsing Data', status: 'pending', progress: 0, message: 'Waiting to start...' },
    { name: 'Validating Records', status: 'pending', progress: 0, message: 'Waiting to start...' },
    { name: 'Saving to Firebase', status: 'pending', progress: 0, message: 'Waiting to start...' }
  ])

  const updateStep = (stepIndex: number, updates: Partial<ProcessingStep>) => {
    setProcessingSteps(prev => prev.map((step, index) => 
      index === stepIndex ? { ...step, ...updates } : step
    ))
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      // Check if it's a CSV file
      if (selectedFile.type === 'text/csv' || selectedFile.name.endsWith('.csv')) {
        setFile(selectedFile)
        setError(null)
        setSuccess(null)
        // Reset processing steps
        setProcessingSteps([
          { name: 'Reading CSV File', status: 'pending', progress: 0, message: 'Waiting to start...' },
          { name: 'Parsing Data', status: 'pending', progress: 0, message: 'Waiting to start...' },
          { name: 'Validating Records', status: 'pending', progress: 0, message: 'Waiting to start...' },
          { name: 'Saving to Firebase', status: 'pending', progress: 0, message: 'Waiting to start...' }
        ])
      } else {
        setError('Please select a valid CSV file. For Excel files, please convert them to CSV first.')
        setFile(null)
      }
    }
  }

  const processCSV = async () => {
    if (!file || !currentUser) return

    setUploading(true)
    setError(null)
    setSuccess(null)

    try {
      // Step 1: Reading CSV File
      updateStep(0, { status: 'processing', progress: 0, message: 'Reading file content...' })
      const text = await file.text()
      updateStep(0, { status: 'completed', progress: 100, message: 'File read successfully' })

      // Step 2: Parsing Data
      updateStep(1, { status: 'processing', progress: 0, message: 'Splitting into lines...' })
      const lines = text.split('\n')
      updateStep(1, { progress: 30, message: 'Extracting headers...' })
      
      const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
      updateStep(1, { progress: 60, message: 'Processing data rows...' })
      
      const data = lines.slice(1)
        .filter(line => line.trim())
        .map((line, index) => {
          const values = line.split(',').map(v => v.trim().replace(/"/g, ''))
          const row: any = {}
          
          headers.forEach((header, i) => {
            row[header] = values[i] || ''
          })
          
          return row
        })

      updateStep(1, { status: 'completed', progress: 100, message: `Parsed ${data.length} rows` })
      setProcessedData(data)

      // Step 3: Validating Records
      updateStep(2, { status: 'processing', progress: 0, message: 'Validating data format...' })
      const validRecords = data.filter(row => {
        const date = row.date || row.Date || row.DATE
        const item = row.item || row.Item || row.ITEM || row.product || row.Product
        const quantity = parseFloat(row.quantity || row.Quantity || row.QUANTITY || row.qty || row.Qty || '0') || 0
        const revenue = parseFloat(row.revenue || row.Revenue || row.REVENUE || row.sales || row.Sales || row.price || row.Price || '0') || 0
        
        return date && item && (quantity > 0 || revenue > 0)
      })
      
      updateStep(2, { status: 'completed', progress: 100, message: `${validRecords.length} valid records found` })

      // Step 4: Saving to Firebase via Backend API (MUCH FASTER!)
      updateStep(3, { status: 'processing', progress: 0, message: 'Uploading to backend for batch processing...' })
      
      const result = await ApiService.uploadCSV(file)
      
      if (result.success) {
        updateStep(3, { status: 'completed', progress: 100, message: `Successfully saved ${result.data.records_count} records` })
        setSuccess(`Successfully processed ${result.data.records_count} records! Total sales: $${result.data.total_sales.toFixed(2)}`)
        
        // Track uploaded file in app state
        if (file) {
          addUploadedFile(file.name)
        }
      } else {
        throw new Error(result.error || 'Upload failed')
      }
      
      if (onDataProcessed) {
        // Convert the processed data to the expected format
        const csvData = {
          headers: headers,
          rows: data.map(row => headers.map(header => row[header] || '')),
          preview: data.slice(0, 5).map(row => headers.map(header => row[header] || ''))
        }
        onDataProcessed(csvData)
      }
      
    } catch (error) {
      console.error('Error processing CSV:', error)
      const errorMessage = `Error processing CSV file: ${error instanceof Error ? error.message : 'Unknown error'}`
      setError(errorMessage)
      
      if (onError) {
        onError(errorMessage)
      }
      
      // Mark current step as error
      const currentStepIndex = processingSteps.findIndex(step => step.status === 'processing')
      if (currentStepIndex !== -1) {
        updateStep(currentStepIndex, { 
          status: 'error', 
          message: 'An error occurred during processing' 
        })
      }
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && (droppedFile.type === 'text/csv' || droppedFile.name.endsWith('.csv'))) {
      setFile(droppedFile)
      setError(null)
      setSuccess(null)
      // Reset processing steps
      setProcessingSteps([
        { name: 'Reading CSV File', status: 'pending', progress: 0, message: 'Waiting to start...' },
        { name: 'Parsing Data', status: 'pending', progress: 0, message: 'Waiting to start...' },
        { name: 'Validating Records', status: 'pending', progress: 0, message: 'Waiting to start...' },
        { name: 'Saving to Firebase', status: 'pending', progress: 0, message: 'Waiting to start...' }
      ])
    } else {
      setError('Please drop a valid CSV file.')
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const getStepIcon = (step: ProcessingStep) => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'processing':
        return <Loader className="h-5 w-5 text-blue-600 animate-spin" />
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-600" />
      default:
        return <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
    }
  }

  const getStepIconForName = (name: string) => {
    if (name.includes('Reading') || name.includes('File')) return <FileSpreadsheet className="h-4 w-4" />
    if (name.includes('Parsing') || name.includes('Data')) return <FileText className="h-4 w-4" />
    if (name.includes('Validating')) return <CheckCircle className="h-4 w-4" />
    if (name.includes('Saving') || name.includes('Firebase')) return <Database className="h-4 w-4" />
    return <div className="h-4 w-4" />
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Sales Data</h3>
        
        <div className="space-y-4">
          {/* File Upload Area */}
          <div
            className={`border-2 border-dashed rounded-lg p-6 text-center ${
              file ? 'border-green-300 bg-green-50' : 'border-gray-300 hover:border-gray-400'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
              id="csv-upload"
            />
            <label htmlFor="csv-upload" className="cursor-pointer">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-600">
                {file ? file.name : 'Click to upload or drag and drop'}
              </p>
              <p className="text-xs text-gray-500">
                CSV files only. For Excel files, convert to CSV first.
              </p>
            </label>
          </div>

          {/* Processing Progress */}
          {uploading && (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-blue-900 mb-3">Processing Progress</h4>
                <div className="space-y-3">
                  {processingSteps.map((step, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          {getStepIcon(step)}
                          <span className="text-sm font-medium text-gray-700">{step.name}</span>
                        </div>
                        <span className="text-sm text-gray-500">{step.progress}%</span>
                      </div>
                      
                      {/* Progress Bar */}
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-300 ${
                            step.status === 'completed' ? 'bg-green-500' :
                            step.status === 'processing' ? 'bg-blue-500' :
                            step.status === 'error' ? 'bg-red-500' : 'bg-gray-300'
                          }`}
                          style={{ width: `${step.progress}%` }}
                        />
                      </div>
                      
                      {/* Status Message */}
                      <p className="text-xs text-gray-600 ml-7">{step.message}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-md">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="flex items-center space-x-2 p-3 bg-green-50 border border-green-200 rounded-md">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <p className="text-sm text-green-600">{success}</p>
            </div>
          )}

          {/* Upload Button */}
          {file && (
            <button
              onClick={processCSV}
              disabled={uploading}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              {uploading ? (
                <>
                  <Loader className="h-4 w-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <FileText className="h-4 w-4" />
                  <span>Process and Save to Firebase</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Data Preview */}
      {processedData.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Preview</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {Object.keys(processedData[0] || {}).map((header) => (
                    <th
                      key={header}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {processedData.slice(0, 5).map((row, index) => (
                  <tr key={index}>
                    {Object.values(row).map((value: any, i) => (
                      <td key={i} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {value}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {processedData.length > 5 && (
            <p className="text-sm text-gray-500 mt-2">
              Showing first 5 rows of {processedData.length} total rows
            </p>
          )}
        </div>
      )}

      {/* Instructions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Instructions</h3>
        <div className="space-y-3 text-sm text-gray-600">
          <p>
            <strong>CSV Format:</strong> Your CSV should include columns for date, item, quantity, and revenue.
          </p>
          <p>
            <strong>Supported Column Names:</strong>
          </p>
          <ul className="list-disc list-inside space-y-1 ml-4">
            <li>Date: date, Date, DATE</li>
            <li>Item: item, Item, ITEM, product, Product</li>
            <li>Quantity: quantity, Quantity, QUANTITY, qty, Qty</li>
            <li>Revenue: revenue, Revenue, REVENUE, sales, Sales, price, Price</li>
          </ul>
          <p>
            <strong>Excel Files:</strong> If you have an Excel file (.xls or .xlsx), please convert it to CSV format first using Excel, Google Sheets, or Numbers.
          </p>
          <p className="text-blue-600 font-medium">
            <strong>🚀 Performance:</strong> This upload now uses optimized batch processing and should be 10-50x faster than before!
          </p>
        </div>
      </div>
    </div>
  )
} 