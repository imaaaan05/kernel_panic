// ============================================================
// Smart Demand Signals — Data Engine
// 100% rule-based statistical engine (no ML black boxes)
// Mirrors the Pandas pipeline described in app.py exactly
// ============================================================

export interface RawRow {
  Client_ID: string;
  Date: string;
  Product_Family: string;
  Quantity: number;
  Transaction_Value: number;
  Client_Potential: number;
  Analytical_Block: string;
}

export interface Alert {
  id: string;
  Client_ID: string;
  Product_Family: string;
  Analytical_Block: string;
  Motivo: string;
  Nivel_de_Riesgo: number;
  Days_Since_Last: number;
  Valor_Oportunidad: number;
  Average_Monthly_Spend: number;
  Loyalty_Factor: string;
  Mean_Days: number;
  Std_Days: number;
  Mean_Qty: number;
  Std_Qty: number;
  Last_Qty: number;
  Average_Transaction_Value: number;
  Days_Delayed: number;
  Register_Action: string;
}

// ─── STEP 1: Parse European CSV string ────────────────────────────────────────
export function parseEuropeanCSV(rawText: string): RawRow[] {
  const lines = rawText.split(/\r?\n/).filter((l) => l.trim().length > 0);
  if (lines.length < 2) return [];

  // Detect separator
  const header = lines[0];
  const sep = header.includes(';') ? ';' : ',';

  const headers = header.split(sep).map((h) => h.trim().replace(/^"|"$/g, ''));

  // Column rename map
  const renameMap: Record<string, string> = {
    'Id.Cliente': 'Client_ID',
    'Fecha': 'Date',
    'Familia_H': 'Product_Family',
    'Unidades': 'Quantity',
    'Valores_H': 'Transaction_Value',
    'Potencial_H': 'Client_Potential',
    'Bloque analítico': 'Analytical_Block',
    // Also handle already-English headers
    Client_ID: 'Client_ID',
    Date: 'Date',
    Product_Family: 'Product_Family',
    Quantity: 'Quantity',
    Transaction_Value: 'Transaction_Value',
    Client_Potential: 'Client_Potential',
    Analytical_Block: 'Analytical_Block',
  };

  const mappedHeaders = headers.map((h) => renameMap[h] ?? h);

  const rows: RawRow[] = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim()) continue;

    // Split by separator respecting quoted fields
    const parts = splitCSVLine(line, sep);

    const obj: Record<string, string> = {};
    mappedHeaders.forEach((col, idx) => {
      obj[col] = (parts[idx] ?? '').trim().replace(/^"|"$/g, '');
    });

    // CRITICAL: Replace commas with dots for European decimals
    const parseEuropeanNum = (val: string): number => {
      const cleaned = val.replace(/\./g, '').replace(',', '.');
      const n = parseFloat(cleaned);
      return isNaN(n) ? NaN : n;
    };

    // Standardize Analytical_Block
    let block = obj['Analytical_Block'] ?? '';
    if (block === 'Productos Técnicos' || block === 'Productos T\u00e9cnicos') {
      block = 'Technical';
    }

    // Parse date
    const rawDate = obj['Date'] ?? '';
    const parsedDate = parseDate(rawDate);
    if (!parsedDate) continue;

    const qty = parseEuropeanNum(obj['Quantity'] ?? '');
    const txVal = parseEuropeanNum(obj['Transaction_Value'] ?? '');
    const potential = parseEuropeanNum(obj['Client_Potential'] ?? '');

    // Remove rows where Quantity or Transaction_Value <= 0
    if (isNaN(qty) || isNaN(txVal) || qty <= 0 || txVal <= 0) continue;

    rows.push({
      Client_ID: obj['Client_ID'] ?? '',
      Date: parsedDate,
      Product_Family: obj['Product_Family'] ?? '',
      Quantity: qty,
      Transaction_Value: txVal,
      Client_Potential: isNaN(potential) ? 0 : potential,
      Analytical_Block: block,
    });
  }

  return rows;
}

function splitCSVLine(line: string, sep: string): string[] {
  const result: string[] = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      inQuotes = !inQuotes;
    } else if (ch === sep && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += ch;
    }
  }
  result.push(current);
  return result;
}

function parseDate(raw: string): string | null {
  if (!raw) return null;
  // Try DD/MM/YYYY
  const dmY = raw.match(/^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})$/);
  if (dmY) {
    const d = dmY[1].padStart(2, '0');
    const m = dmY[2].padStart(2, '0');
    const y = dmY[3];
    return `${y}-${m}-${d}`;
  }
  // Try YYYY-MM-DD
  const yMD = raw.match(/^(\d{4})[\/\-](\d{2})[\/\-](\d{2})$/);
  if (yMD) return raw;
  // Try DD-MM-YYYY
  const dmy2 = raw.match(/^(\d{1,2})-(\d{1,2})-(\d{4})$/);
  if (dmy2) {
    return `${dmy2[3]}-${dmy2[2].padStart(2, '0')}-${dmy2[1].padStart(2, '0')}`;
  }
  // Try to parse anything else
  const t = new Date(raw);
  if (!isNaN(t.getTime())) {
    return t.toISOString().slice(0, 10);
  }
  return null;
}

// ─── STEP 2: Feature Engineering ──────────────────────────────────────────────

interface ClientStats {
  Client_ID: string;
  Average_Monthly_Spend: number;
  Max_Client_Potential: number;
  Loyalty_Factor: 'Loyal' | 'Promiscuous';
}

function computeLoyaltyFactors(rows: RawRow[]): Map<string, ClientStats> {
  // Group by Client_ID + Month, sum Transaction_Value
  const monthlyMap = new Map<string, Map<string, number>>();
  const potentialMap = new Map<string, number>();

  for (const row of rows) {
    const month = row.Date.slice(0, 7); // YYYY-MM
    if (!monthlyMap.has(row.Client_ID)) monthlyMap.set(row.Client_ID, new Map());
    const mMap = monthlyMap.get(row.Client_ID)!;
    mMap.set(month, (mMap.get(month) ?? 0) + row.Transaction_Value);

    // Track max Client_Potential per client
    const cur = potentialMap.get(row.Client_ID) ?? 0;
    if (row.Client_Potential > cur) potentialMap.set(row.Client_ID, row.Client_Potential);
  }

  const result = new Map<string, ClientStats>();
  for (const [clientId, mMap] of monthlyMap.entries()) {
    const monthlyValues = Array.from(mMap.values());
    const avgMonthlySpend = mean(monthlyValues);
    const maxPotential = potentialMap.get(clientId) ?? 0;
    const loyaltyFactor: 'Loyal' | 'Promiscuous' =
      avgMonthlySpend >= 0.85 * maxPotential ? 'Loyal' : 'Promiscuous';

    result.set(clientId, {
      Client_ID: clientId,
      Average_Monthly_Spend: avgMonthlySpend,
      Max_Client_Potential: maxPotential,
      Loyalty_Factor: loyaltyFactor,
    });
  }
  return result;
}

interface AggRow {
  Client_ID: string;
  Date: string;
  Product_Family: string;
  Quantity: number;
  Transaction_Value: number;
  Analytical_Block: string;
  Loyalty_Factor: string;
  Average_Monthly_Spend: number;
  Days_Between: number | null;
}

function aggregateAndSort(rows: RawRow[], loyaltyMap: Map<string, ClientStats>): AggRow[] {
  // Group by [Client_ID, Date, Product_Family]
  const groupMap = new Map<string, AggRow>();

  for (const row of rows) {
    const key = `${row.Client_ID}|||${row.Date}|||${row.Product_Family}`;
    if (!groupMap.has(key)) {
      const loyalty = loyaltyMap.get(row.Client_ID);
      groupMap.set(key, {
        Client_ID: row.Client_ID,
        Date: row.Date,
        Product_Family: row.Product_Family,
        Quantity: 0,
        Transaction_Value: 0,
        Analytical_Block: row.Analytical_Block,
        Loyalty_Factor: loyalty?.Loyalty_Factor ?? 'Promiscuous',
        Average_Monthly_Spend: loyalty?.Average_Monthly_Spend ?? 0,
        Days_Between: null,
      });
    }
    const agg = groupMap.get(key)!;
    agg.Quantity += row.Quantity;
    agg.Transaction_Value += row.Transaction_Value;
  }

  // Sort per Client_ID + Product_Family chronologically and compute Days_Between
  const sorted = Array.from(groupMap.values()).sort((a, b) => {
    const ka = `${a.Client_ID}|||${a.Product_Family}|||${a.Date}`;
    const kb = `${b.Client_ID}|||${b.Product_Family}|||${b.Date}`;
    return ka.localeCompare(kb);
  });

  // Compute Days_Between
  const lastPurchaseMap = new Map<string, string>(); // key -> last date
  for (const row of sorted) {
    const key = `${row.Client_ID}|||${row.Product_Family}`;
    const last = lastPurchaseMap.get(key);
    if (last) {
      const diff = dateDiffDays(last, row.Date);
      row.Days_Between = diff;
    }
    lastPurchaseMap.set(key, row.Date);
  }

  return sorted;
}

function dateDiffDays(d1: string, d2: string): number {
  const a = new Date(d1).getTime();
  const b = new Date(d2).getTime();
  return Math.round(Math.abs(b - a) / 86400000);
}

// ─── STEP 3: Statistical Engine & Cold Start ──────────────────────────────────

interface PairStats {
  key: string; // Client_ID|||Product_Family
  Client_ID: string;
  Product_Family: string;
  Mean_Qty: number;
  Std_Qty: number;
  Mean_Days: number;
  Std_Days: number;
  Purchase_Count: number;
}

function computePairStats(aggRows: AggRow[]): Map<string, PairStats> {
  // Group by Client_ID + Product_Family
  const groups = new Map<string, AggRow[]>();
  for (const row of aggRows) {
    const key = `${row.Client_ID}|||${row.Product_Family}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(row);
  }

  // Global family stats for cold-start fallback
  const familyGroups = new Map<string, AggRow[]>();
  for (const row of aggRows) {
    if (!familyGroups.has(row.Product_Family)) familyGroups.set(row.Product_Family, []);
    familyGroups.get(row.Product_Family)!.push(row);
  }
  const familyStats = new Map<string, { meanQty: number; stdQty: number; meanDays: number; stdDays: number }>();
  for (const [fam, rows] of familyGroups.entries()) {
    const qtys = rows.map((r) => r.Quantity);
    const days = rows.map((r) => r.Days_Between).filter((d): d is number => d !== null);
    familyStats.set(fam, {
      meanQty: mean(qtys),
      stdQty: std(qtys),
      meanDays: days.length > 0 ? mean(days) : 30,
      stdDays: days.length > 0 ? std(days) : 7,
    });
  }

  const result = new Map<string, PairStats>();
  for (const [key, rows] of groups.entries()) {
    const parts = key.split('|||');
    const clientId = parts[0];
    const family = parts[1];

    const qtys = rows.map((r) => r.Quantity);
    const days = rows.map((r) => r.Days_Between).filter((d): d is number => d !== null);
    const purchaseCount = rows.length;

    let mQty: number, sQty: number, mDays: number, sDays: number;

    if (purchaseCount < 3) {
      // Cold-start: use global family stats
      const fs = familyStats.get(family);
      mQty = fs?.meanQty ?? 0;
      sQty = fs?.stdQty ?? 0;
      mDays = fs?.meanDays ?? 30;
      sDays = fs?.stdDays ?? 7;
    } else {
      mQty = mean(qtys);
      sQty = std(qtys);
      mDays = days.length > 0 ? mean(days) : (familyStats.get(family)?.meanDays ?? 30);
      sDays = days.length > 0 ? std(days) : (familyStats.get(family)?.stdDays ?? 7);
    }

    // Fill NaN with 0
    result.set(key, {
      key,
      Client_ID: clientId,
      Product_Family: family,
      Mean_Qty: mQty || 0,
      Std_Qty: sQty || 0,
      Mean_Days: mDays || 30,
      Std_Days: sDays || 7,
      Purchase_Count: purchaseCount,
    });
  }

  return result;
}

// ─── STEP 4: Alert Logic ──────────────────────────────────────────────────────

export interface ProcessedResult {
  alerts: Alert[];
  totalClients: number;
  totalFamilies: number;
  todayDate: string;
  familyOptions: string[];
  blockOptions: string[];
}

function getMaxDate(rows: RawRow[]): string {
  let max = '';
  for (const row of rows) {
    if (row.Date > max) max = row.Date;
  }
  return max;
}

export function runEngine(rows: RawRow[]): ProcessedResult {
  if (rows.length === 0) {
    return {
      alerts: [],
      totalClients: 0,
      totalFamilies: 0,
      todayDate: new Date().toISOString().slice(0, 10),
      familyOptions: [],
      blockOptions: [],
    };
  }

  const todayStr = getMaxDate(rows);
  const todayMs = new Date(todayStr).getTime();

  // Step 2a: Loyalty
  const loyaltyMap = computeLoyaltyFactors(rows);

  // Step 2b: Aggregate
  const aggRows = aggregateAndSort(rows, loyaltyMap);

  // Step 3: Stats
  const statsMap = computePairStats(aggRows);

  // Get most recent purchase per Client/Family
  const latestMap = new Map<string, AggRow>();
  for (const row of aggRows) {
    const key = `${row.Client_ID}|||${row.Product_Family}`;
    const existing = latestMap.get(key);
    if (!existing || row.Date > existing.Date) {
      latestMap.set(key, row);
    }
  }

  // Average Transaction Value per Client/Family
  const avgTxMap = new Map<string, number>();
  const txGroups = new Map<string, number[]>();
  for (const row of aggRows) {
    const key = `${row.Client_ID}|||${row.Product_Family}`;
    if (!txGroups.has(key)) txGroups.set(key, []);
    txGroups.get(key)!.push(row.Transaction_Value);
  }
  for (const [key, vals] of txGroups.entries()) {
    avgTxMap.set(key, mean(vals));
  }

  // ─── Alert Generation ─────────────────────────────────────
  const rawAlerts: Omit<Alert, 'Nivel_de_Riesgo'>[] = [];

  for (const [key, latestRow] of latestMap.entries()) {
    const stats = statsMap.get(key);
    if (!stats) continue;

    const daysSinceLast = Math.round((todayMs - new Date(latestRow.Date).getTime()) / 86400000);
    const avgTx = avgTxMap.get(key) ?? 0;
    const loyalty = loyaltyMap.get(latestRow.Client_ID);
    const avgMonthlySpend = loyalty?.Average_Monthly_Spend ?? 0;
    const clientPotential = loyalty?.Max_Client_Potential ?? 0;

    const block = latestRow.Analytical_Block;
    const loyaltyFactor = latestRow.Loyalty_Factor;

    // ── Rule A: Commodities ──────────────────────────────────
    if (block === 'Commodities' && loyaltyFactor === 'Promiscuous') {
      if (daysSinceLast >= stats.Mean_Days) {
        const oppValue = Math.max(0, clientPotential - avgMonthlySpend);
        const daysDelayed = Math.max(0, daysSinceLast - stats.Mean_Days);
        rawAlerts.push({
          id: `${key}|||A`,
          Client_ID: latestRow.Client_ID,
          Product_Family: latestRow.Product_Family,
          Analytical_Block: block,
          Motivo: 'Ventana de Captura',
          Days_Since_Last: daysSinceLast,
          Valor_Oportunidad: oppValue,
          Average_Monthly_Spend: avgMonthlySpend,
          Loyalty_Factor: loyaltyFactor,
          Mean_Days: stats.Mean_Days,
          Std_Days: stats.Std_Days,
          Mean_Qty: stats.Mean_Qty,
          Std_Qty: stats.Std_Qty,
          Last_Qty: latestRow.Quantity,
          Average_Transaction_Value: avgTx,
          Days_Delayed: daysDelayed,
          Register_Action: '',
        });
      }
    }

    // ── Rule B: Technical ────────────────────────────────────
    if (block === 'Technical') {
      const expectedDays =
        stats.Mean_Days * (stats.Mean_Qty > 0 ? latestRow.Quantity / stats.Mean_Qty : 1);

      // B1: Time Drop
      if (daysSinceLast > expectedDays + 1.5 * stats.Std_Days) {
        const daysDelayed = Math.max(0, daysSinceLast - expectedDays);
        rawAlerts.push({
          id: `${key}|||B1`,
          Client_ID: latestRow.Client_ID,
          Product_Family: latestRow.Product_Family,
          Analytical_Block: block,
          Motivo: 'Retraso anómalo en tiempo',
          Days_Since_Last: daysSinceLast,
          Valor_Oportunidad: avgMonthlySpend,
          Average_Monthly_Spend: avgMonthlySpend,
          Loyalty_Factor: loyaltyFactor,
          Mean_Days: stats.Mean_Days,
          Std_Days: stats.Std_Days,
          Mean_Qty: stats.Mean_Qty,
          Std_Qty: stats.Std_Qty,
          Last_Qty: latestRow.Quantity,
          Average_Transaction_Value: avgTx,
          Days_Delayed: daysDelayed,
          Register_Action: '',
        });
      }

      // B2: Volume Drop
      if (latestRow.Quantity < stats.Mean_Qty - 1.0 * stats.Std_Qty) {
        const daysDelayed = Math.max(0, daysSinceLast - stats.Mean_Days);
        rawAlerts.push({
          id: `${key}|||B2`,
          Client_ID: latestRow.Client_ID,
          Product_Family: latestRow.Product_Family,
          Analytical_Block: block,
          Motivo: 'Caída drástica de volumen',
          Days_Since_Last: daysSinceLast,
          Valor_Oportunidad: avgMonthlySpend,
          Average_Monthly_Spend: avgMonthlySpend,
          Loyalty_Factor: loyaltyFactor,
          Mean_Days: stats.Mean_Days,
          Std_Days: stats.Std_Days,
          Mean_Qty: stats.Mean_Qty,
          Std_Qty: stats.Std_Qty,
          Last_Qty: latestRow.Quantity,
          Average_Transaction_Value: avgTx,
          Days_Delayed: daysDelayed,
          Register_Action: '',
        });
      }
    }
  }

  // ─── Step 5: Prioritization Score ─────────────────────────
  const rawScores = rawAlerts.map((a) => {
    const meanDays = a.Mean_Days || 1;
    return a.Average_Transaction_Value * (1 + a.Days_Delayed / meanDays);
  });

  const minScore = Math.min(...rawScores);
  const maxScore = Math.max(...rawScores);
  const range = maxScore - minScore || 1;

  const alerts: Alert[] = rawAlerts.map((a, idx) => {
    const normalized = ((rawScores[idx] - minScore) / range) * 99 + 1;
    return {
      ...a,
      Nivel_de_Riesgo: Math.round(normalized),
    };
  });

  // Sort by Nivel_de_Riesgo desc
  alerts.sort((a, b) => b.Nivel_de_Riesgo - a.Nivel_de_Riesgo);

  const familyOptions = Array.from(new Set(rows.map((r) => r.Product_Family))).sort();
  const blockOptions = Array.from(new Set(rows.map((r) => r.Analytical_Block))).sort();
  const totalClients = new Set(rows.map((r) => r.Client_ID)).size;
  const totalFamilies = familyOptions.length;

  return { alerts, totalClients, totalFamilies, todayDate: todayStr, familyOptions, blockOptions };
}

// ─── Utility Math ─────────────────────────────────────────────────────────────
function mean(arr: number[]): number {
  if (arr.length === 0) return 0;
  return arr.reduce((s, v) => s + v, 0) / arr.length;
}

function std(arr: number[]): number {
  if (arr.length < 2) return 0;
  const m = mean(arr);
  const variance = arr.reduce((s, v) => s + (v - m) ** 2, 0) / (arr.length - 1);
  return Math.sqrt(variance);
}

// ─── Demo Data Generator ───────────────────────────────────────────────────────
export function generateDemoData(): RawRow[] {
  const families = [
    { name: 'Gloves Nitrile', block: 'Commodities' },
    { name: 'Surgical Masks', block: 'Commodities' },
    { name: 'IV Catheters', block: 'Technical' },
    { name: 'Suture Kit Pro', block: 'Technical' },
    { name: 'Syringes 5ml', block: 'Commodities' },
    { name: 'Compression Bandages', block: 'Technical' },
    { name: 'Disinfectant Gel', block: 'Commodities' },
    { name: 'Surgical Drapes', block: 'Technical' },
  ];

  const clients = [
    { id: 'CLI-0001', potential: 18000 },
    { id: 'CLI-0002', potential: 25000 },
    { id: 'CLI-0003', potential: 12000 },
    { id: 'CLI-0004', potential: 32000 },
    { id: 'CLI-0005', potential: 9500 },
    { id: 'CLI-0006', potential: 41000 },
    { id: 'CLI-0007', potential: 15500 },
    { id: 'CLI-0008', potential: 28000 },
    { id: 'CLI-0009', potential: 7800 },
    { id: 'CLI-0010', potential: 55000 },
    { id: 'CLI-0011', potential: 22000 },
    { id: 'CLI-0012', potential: 18500 },
  ];

  const rows: RawRow[] = [];
  const today = new Date('2024-10-15');

  for (const client of clients) {
    const assignedFamilies = families.slice(0, 4 + Math.floor(Math.random() * 4));

    for (const fam of assignedFamilies) {
      const purchaseCount = 4 + Math.floor(Math.random() * 8);
      const baseQty = 50 + Math.floor(Math.random() * 200);
      const baseValue = 500 + Math.floor(Math.random() * 3000);
      const avgInterval = 20 + Math.floor(Math.random() * 25);

      let currentDate = new Date(today);
      currentDate.setDate(currentDate.getDate() - purchaseCount * avgInterval - Math.floor(Math.random() * 60));

      for (let p = 0; p < purchaseCount; p++) {
        const isLastPurchase = p === purchaseCount - 1;
        const isAnomalous = isLastPurchase && Math.random() < 0.35;

        const qty = isAnomalous
          ? baseQty * (0.2 + Math.random() * 0.3)
          : baseQty * (0.7 + Math.random() * 0.6);

        const txVal = qty * (baseValue / baseQty) * (0.9 + Math.random() * 0.2);

        const dateStr = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(currentDate.getDate()).padStart(2, '0')}`;

        // For some clients, make the last purchase very old (churn signal)
        const isStale = isLastPurchase && Math.random() < 0.4;
        const daysToAdd = isStale
          ? avgInterval + 20 + Math.floor(Math.random() * 40)
          : Math.max(5, avgInterval + Math.floor((Math.random() - 0.5) * 15));

        rows.push({
          Client_ID: client.id,
          Date: dateStr,
          Product_Family: fam.name,
          Quantity: Math.max(1, Math.round(qty)),
          Transaction_Value: Math.max(10, Math.round(txVal)),
          Client_Potential: client.potential,
          Analytical_Block: fam.block,
        });

        currentDate.setDate(currentDate.getDate() + daysToAdd);
      }
    }
  }

  return rows;
}
