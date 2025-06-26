import { useState } from 'react'
import { Upload, FileText, AlertCircle, CheckCircle, Loader, Database } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { addInventoryItem, InventoryItem } from '../services/firebaseService'

interface ProcessingStep {
  name: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  progress: number
  message: string
}

interface InventoryImportProps {
  onImportComplete?: (count: number) => void
  onError?: (error: string) => void
}

export default function InventoryImport({ onImportComplete, onError }: InventoryImportProps) {
  const { currentUser } = useAuth()
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [processingSteps, setProcessingSteps] = useState<ProcessingStep[]>([
    { name: 'Reading CSV File', status: 'pending', progress: 0, message: 'Waiting to start...' },
    { name: 'Parsing Data', status: 'pending', progress: 0, message: 'Waiting to start...' },
    { name: 'Validating Records', status: 'pending', progress: 0, message: 'Waiting to start...' },
    { name: 'Saving to Database', status: 'pending', progress: 0, message: 'Waiting to start...' }
  ])

  const updateStep = (stepIndex: number, updates: Partial<ProcessingStep>) => {
    setProcessingSteps(prev => prev.map((step, index) => 
      index === stepIndex ? { ...step, ...updates } : step
    ))
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (selectedFile.type === 'text/csv' || selectedFile.name.endsWith('.csv')) {
        setFile(selectedFile)
        setError(null)
        setSuccess(null)
        setProcessingSteps([
          { name: 'Reading CSV File', status: 'pending', progress: 0, message: 'Waiting to start...' },
          { name: 'Parsing Data', status: 'pending', progress: 0, message: 'Waiting to start...' },
          { name: 'Validating Records', status: 'pending', progress: 0, message: 'Waiting to start...' },
          { name: 'Saving to Database', status: 'pending', progress: 0, message: 'Waiting to start...' }
        ])
      } else {
        setError('Please select a valid CSV file.')
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

      // Step 3: Validating Records
      updateStep(2, { status: 'processing', progress: 0, message: 'Validating data format...' })
      const validRecords = data.filter(row => {
        const name = row.name || row.Name || row.NAME
        const category = row.category || row.Category || row.CATEGORY
        const currentStock = parseFloat(row.currentStock || row.CurrentStock || row.CURRENTSTOCK || '0') || 0
        const minStock = parseFloat(row.minStock || row.MinStock || row.MINSTOCK || '0') || 0
        const maxStock = parseFloat(row.maxStock || row.MaxStock || row.MAXSTOCK || '0') || 0
        const unit = row.unit || row.Unit || row.UNIT
        const costPerUnit = parseFloat(row.costPerUnit || row.CostPerUnit || row.COSTPERUNIT || '0') || 0
        
        return name && category && unit && costPerUnit > 0
      })
      
      updateStep(2, { status: 'completed', progress: 100, message: `${validRecords.length} valid records found` })

      // Step 4: Saving to Database
      updateStep(3, { status: 'processing', progress: 0, message: 'Saving items to database...' })
      
      let savedCount = 0
      for (let i = 0; i < validRecords.length; i++) {
        const record = validRecords[i]
        
        const inventoryItem: Omit<InventoryItem, 'id' | 'lastUpdated'> = {
          name: record.name || record.Name || record.NAME,
          category: record.category || record.Category || record.CATEGORY,
          currentStock: parseFloat(record.currentStock || record.CurrentStock || record.CURRENTSTOCK || '0') || 0,
          minStock: parseFloat(record.minStock || record.MinStock || record.MINSTOCK || '0') || 0,
          maxStock: parseFloat(record.maxStock || record.MaxStock || record.MAXSTOCK || '0') || 100,
          unit: record.unit || record.Unit || record.UNIT,
          costPerUnit: parseFloat(record.costPerUnit || record.CostPerUnit || record.COSTPERUNIT || '0') || 0,
          supplierId: record.supplierId || record.SupplierId || record.SUPPLIERID || '',
          userId: currentUser.uid
        }
        
        await addInventoryItem(inventoryItem)
        savedCount++
        
        // Update progress
        const progress = Math.round((i + 1) / validRecords.length * 100)
        updateStep(3, { progress, message: `Saved ${savedCount} of ${validRecords.length} items` })
      }
      
      updateStep(3, { status: 'completed', progress: 100, message: `Successfully saved ${savedCount} items` })
      setSuccess(`Successfully imported ${savedCount} inventory items!`)
      
      if (onImportComplete) {
        onImportComplete(savedCount)
      }
      
    } catch (error) {
      console.error('Error processing inventory CSV:', error)
      const errorMessage = `Error processing inventory CSV: ${error instanceof Error ? error.message : 'Unknown error'}`
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

  return (
    <div className="space-y-6">
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Bulk Import Inventory</h3>
        
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
              id="inventory-csv-upload"
            />
            <label htmlFor="inventory-csv-upload" className="cursor-pointer">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-600">
                {file ? file.name : 'Click to upload or drag and drop'}
              </p>
              <p className="text-xs text-gray-500">CSV files only</p>
            </label>
          </div>

          {/* Process Button */}
          {file && (
            <button
              onClick={processCSV}
              disabled={uploading}
              className="w-full btn-primary flex items-center justify-center space-x-2"
            >
              {uploading ? (
                <>
                  <Loader className="h-4 w-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Database className="h-4 w-4" />
                  <span>Import Inventory Items</span>
                </>
              )}
            </button>
          )}

          {/* Processing Steps */}
          {uploading && (
            <div className="space-y-3">
              {processingSteps.map((step, index) => (
                <div key={index} className="flex items-center space-x-3">
                  {getStepIcon(step)}
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{step.name}</p>
                    <p className="text-xs text-gray-500">{step.message}</p>
                    {step.status === 'processing' && (
                      <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${step.progress}%` }}
                        ></div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start space-x-2">
                <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
                <div>
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <p className="mt-1 text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Success Display */}
          {success && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                <div>
                  <h3 className="text-sm font-medium text-green-800">Success</h3>
                  <p className="mt-1 text-sm text-green-700">{success}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* CSV Format Instructions */}
      <div className="card">
        <h4 className="text-md font-semibold text-gray-900 mb-3">CSV Format Requirements</h4>
        <div className="text-sm text-gray-600 space-y-2">
          <p><strong>Required columns:</strong> name, category, currentStock, minStock, maxStock, unit, costPerUnit</p>
          <p><strong>Optional columns:</strong> supplierId</p>
          <p><strong>Example:</strong></p>
          <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto">
{`name,category,currentStock,minStock,maxStock,unit,costPerUnit,supplierId
Coffee Beans,Beverages,25,10,50,kg,12.50,
Milk,Dairy,15,5,30,l,2.80,`}
          </pre>
        </div>
      </div>
    </div>
  )
} 