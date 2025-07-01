/**
 * Interfaces e tipos compartilhados da aplicação
 */

export interface Attribute {
  name: string;
  type: string;
  table?: string;
  qualified_name?: string;
}

export interface Join {
  targetTable: string;
  sourceAttribute: string;
  targetAttribute: string;
  joinType: string;
  isTransitive?: boolean;
  intermediateJoins?: Join[];
}

export interface AggregateFunction {
  function: string;
  attribute: string;
  alias: string;
}

export interface OrderByColumn {
  attribute?: string;
  column?: string;
  direction: 'ASC' | 'DESC';
}



export interface ReportRequest {
  baseTable: string;
  attributes: string[];
  joins: Join[];
  groupByAttributes: string[];
  aggregateFunctions: AggregateFunction[];
  orderByColumns: OrderByColumn[];
  filters: Filter[];
  limit?: number;
}

export interface TableRelations {
  direct: string[];
  transitive: Record<string, any[]>;
}

export interface ReportResponse {
  data: any[];
  sql: string;
}

export interface ApiResponse<T> {
  [key: string]: T;
}

// Tipos utilitários
export type JoinType = 'INNER JOIN' | 'LEFT JOIN' | 'RIGHT JOIN' | 'FULL JOIN';

export type SortDirection = 'ASC' | 'DESC';

export type FilterOperator = '=' | '!=' | '>' | '<' | '>=' | '<=' | 'LIKE' | 'ILIKE' | 'IN' | 'NOT IN';

export type AggregateFunctionType = 'COUNT' | 'SUM' | 'AVG' | 'MIN' | 'MAX';

// Constantes
export const JOIN_TYPES: Array<{ text: string; value: JoinType }> = [
  { text: "Inner Join", value: "INNER JOIN" },
  { text: "Left Join", value: "LEFT JOIN" },
  { text: "Right Join", value: "RIGHT JOIN" },
  { text: "Full Join", value: "FULL JOIN" },
];

export const SORT_DIRECTIONS: Array<{ title: string; value: SortDirection }> = [
  { title: 'Ascendente', value: 'ASC' },
  { title: 'Descendente', value: 'DESC' }
];

export const AGGREGATE_FUNCTIONS: Array<{ text: string; value: AggregateFunctionType }> = [
  { text: "Contar", value: "COUNT" },
  { text: "Somar", value: "SUM" },
  { text: "Média", value: "AVG" },
  { text: "Mínimo", value: "MIN" },
  { text: "Máximo", value: "MAX" },
];

export interface OrderBy {
  attribute: string;
  direction: 'ASC' | 'DESC';
}

export interface Filter {
  attribute: string;
  operator: string;
  value: any;
  logic: 'AND' | 'OR';
  function?: string; // Função SQL opcional (UPPER, LOWER, etc.)
}
