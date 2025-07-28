"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Package, TrendingUp, TrendingDown, BarChart3 } from "lucide-react"

interface Product {
  id: string
  name: string
  sku: string
  description: string
  currentStock: number
  minStock: number
  maxStock: number
}

interface Transaction {
  id: string
  type: "IN" | "OUT"
  date: string
  reference: string
  totalItems: number
}

interface TransactionDetail {
  id: string
  transactionId: string
  productId: string
  quantity: number
  unitPrice: number
  product?: Product
}

export default function WarehouseInventory() {
  const [products, setProducts] = useState<Product[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [transactionDetails, setTransactionDetails] = useState<TransactionDetail[]>([])
  const [loading, setLoading] = useState(false)


  const [newProduct, setNewProduct] = useState({
    name: "",
    sku: "",
    description: "",
    minStock: 0,
    maxStock: 100,
  })

  const [newTransaction, setNewTransaction] = useState({
    type: "IN" as "IN" | "OUT",
    reference: "",
    items: [{ productId: "", quantity: 0, unitPrice: 0 }],
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [productsRes, transactionsRes, detailsRes] = await Promise.all([
        fetch("/api/products"),
        fetch("/api/transactions"),
        fetch("/api/transaction-details"),
      ])

      if (productsRes.ok) setProducts(await productsRes.json())
      if (transactionsRes.ok) setTransactions(await transactionsRes.json())
      if (detailsRes.ok) setTransactionDetails(await detailsRes.json())
    } catch (error) {
      console.error("Error loading data:", error)
    } finally {
      setLoading(false)
    }
  }

  const addProduct = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newProduct.name || !newProduct.sku) return

    try {
      const response = await fetch("/api/products", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...newProduct, currentStock: 0 }),
      })

      if (response.ok) {
        setNewProduct({ name: "", sku: "", description: "", minStock: 0, maxStock: 100 })
        loadData()
      }
    } catch (error) {
      console.error("Error adding product:", error)
    }
  }

  const addTransaction = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTransaction.reference || newTransaction.items.some((item) => !item.productId || item.quantity <= 0)) return

    try {
      const response = await fetch("/api/transactions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newTransaction),
      })

      if (response.ok) {
        setNewTransaction({
          type: "IN",
          reference: "",
          items: [{ productId: "", quantity: 0, unitPrice: 0 }],
        })
        loadData()
      }
    } catch (error) {
      console.error("Error adding transaction:", error)
    }
  }

  const getStockStatus = (product: Product) => {
    if (product.currentStock <= product.minStock) return "low"
    if (product.currentStock >= product.maxStock) return "high"
    return "normal"
  }

  const getStockBadge = (status: string) => {
    switch (status) {
      case "low":
        return <Badge variant="destructive">Low Stock</Badge>
      case "high":
        return <Badge variant="secondary">High Stock</Badge>
      default:
        return <Badge variant="default">Normal</Badge>
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center gap-2 mb-6">
        <Package className="h-8 w-8" />
        <h1 className="text-3xl font-bold">Warehouse Inventory System</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Products</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{products.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Stock</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{products.reduce((sum, p) => sum + p.currentStock, 0)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Low Stock Items</CardTitle>
            <TrendingDown className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{products.filter((p) => p.currentStock <= p.minStock).length}</div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="inventory" className="space-y-4">
        <TabsList>
          <TabsTrigger value="inventory">Current Inventory</TabsTrigger>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="add-product">Add Product</TabsTrigger>
          <TabsTrigger value="add-transaction">New Transaction</TabsTrigger>
        </TabsList>

        <TabsContent value="inventory">
          <Card>
            <CardHeader>
              <CardTitle>Current Inventory</CardTitle>
              <CardDescription>View all products and their current stock levels</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>SKU</TableHead>
                    <TableHead>Product Name</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Current Stock</TableHead>
                    <TableHead>Min/Max</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {products.map((product) => (
                    <TableRow key={product.id}>
                      <TableCell className="font-medium">{product.sku}</TableCell>
                      <TableCell>{product.name}</TableCell>
                      <TableCell>{product.description}</TableCell>
                      <TableCell className="text-center font-bold">{product.currentStock}</TableCell>
                      <TableCell>
                        {product.minStock} / {product.maxStock}
                      </TableCell>
                      <TableCell>{getStockBadge(getStockStatus(product))}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="transactions">
          <Card>
            <CardHeader>
              <CardTitle>Recent Transactions</CardTitle>
              <CardDescription>View all stock movements</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Reference</TableHead>
                    <TableHead>Total Items</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {transactions.map((transaction) => (
                    <TableRow key={transaction.id}>
                      <TableCell>{new Date(transaction.date).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <Badge variant={transaction.type === "IN" ? "default" : "secondary"}>
                          {transaction.type === "IN" ? (
                            <>
                              <TrendingUp className="w-3 h-3 mr-1" /> IN
                            </>
                          ) : (
                            <>
                              <TrendingDown className="w-3 h-3 mr-1" /> OUT
                            </>
                          )}
                        </Badge>
                      </TableCell>
                      <TableCell>{transaction.reference}</TableCell>
                      <TableCell>{transaction.totalItems}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="add-product">
          <Card>
            <CardHeader>
              <CardTitle>Add New Product</CardTitle>
              <CardDescription>Register a new product in the system</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={addProduct} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Product Name *</Label>
                    <Input
                      id="name"
                      value={newProduct.name}
                      onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="sku">SKU *</Label>
                    <Input
                      id="sku"
                      value={newProduct.sku}
                      onChange={(e) => setNewProduct({ ...newProduct, sku: e.target.value })}
                      required
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={newProduct.description}
                    onChange={(e) => setNewProduct({ ...newProduct, description: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="minStock">Minimum Stock</Label>
                    <Input
                      id="minStock"
                      type="number"
                      min="0"
                      value={newProduct.minStock}
                      onChange={(e) => setNewProduct({ ...newProduct, minStock: Number.parseInt(e.target.value) || 0 })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="maxStock">Maximum Stock</Label>
                    <Input
                      id="maxStock"
                      type="number"
                      min="1"
                      value={newProduct.maxStock}
                      onChange={(e) =>
                        setNewProduct({ ...newProduct, maxStock: Number.parseInt(e.target.value) || 100 })
                      }
                    />
                  </div>
                </div>
                <Button type="submit" className="w-full">
                  Add Product
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="add-transaction">
          <Card>
            <CardHeader>
              <CardTitle>New Stock Transaction</CardTitle>
              <CardDescription>Record stock in/out movements</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={addTransaction} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="type">Transaction Type</Label>
                    <Select
                      value={newTransaction.type}
                      onValueChange={(value: "IN" | "OUT") => setNewTransaction({ ...newTransaction, type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="IN">Stock In</SelectItem>
                        <SelectItem value="OUT">Stock Out</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="reference">Reference *</Label>
                    <Input
                      id="reference"
                      value={newTransaction.reference}
                      onChange={(e) => setNewTransaction({ ...newTransaction, reference: e.target.value })}
                      placeholder="PO-001, SO-001, etc."
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Transaction Items</Label>
                  {newTransaction.items.map((item, index) => (
                    <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-2 p-3 border rounded">
                      <Select
                        value={item.productId}
                        onValueChange={(value) => {
                          const items = [...newTransaction.items]
                          items[index].productId = value
                          setNewTransaction({ ...newTransaction, items })
                        }}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select Product" />
                        </SelectTrigger>
                        <SelectContent>
                          {products.map((product) => (
                            <SelectItem key={product.id} value={product.id}>
                              {product.name} ({product.sku})
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <Input
                        type="number"
                        min="1"
                        placeholder="Quantity"
                        value={item.quantity || ""}
                        onChange={(e) => {
                          const items = [...newTransaction.items]
                          items[index].quantity = Number.parseInt(e.target.value) || 0
                          setNewTransaction({ ...newTransaction, items })
                        }}
                      />
                      <Input
                        type="number"
                        min="0"
                        step="0.01"
                        placeholder="Unit Price"
                        value={item.unitPrice || ""}
                        onChange={(e) => {
                          const items = [...newTransaction.items]
                          items[index].unitPrice = Number.parseFloat(e.target.value) || 0
                          setNewTransaction({ ...newTransaction, items })
                        }}
                      />
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                          const items = newTransaction.items.filter((_, i) => i !== index)
                          setNewTransaction({ ...newTransaction, items })
                        }}
                        disabled={newTransaction.items.length === 1}
                      >
                        Remove
                      </Button>
                    </div>
                  ))}
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setNewTransaction({
                        ...newTransaction,
                        items: [...newTransaction.items, { productId: "", quantity: 0, unitPrice: 0 }],
                      })
                    }}
                  >
                    Add Item
                  </Button>
                </div>

                <Button type="submit" className="w-full">
                  Record Transaction
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
