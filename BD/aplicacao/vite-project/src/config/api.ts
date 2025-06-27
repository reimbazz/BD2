/**
 * Configuração centralizada da API
 */
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/api/db',
  ENDPOINTS: {
    TABLES: '/tables',
    TABLE_COLUMNS: (tableName: string) => `/tables/${tableName}/columns`,
    TABLE_RELATIONS: (tableName: string) => `/tables/${tableName}/relations`,
    TRANSITIVE_RELATIONS: (tableName: string) => `/tables/${tableName}/transitive-relations`,
    TRANSITIVE_RELATIONS_WITH_JOINS: (tableName: string) => `/tables/${tableName}/transitive-relations-with-joins`,
    FOREIGN_KEYS: (sourceTable: string, targetTable: string) => `/tables/${sourceTable}/foreign-keys/${targetTable}`,
    JOINED_COLUMNS: '/tables/joined-columns',
    REPORT: '/report',
    FUNCTIONS: '/functions/available'
  }
} as const;

/**
 * Utilitário para construir URLs da API
 */
export class ApiUrlBuilder {
  static getTables(): string {
    return `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TABLES}`;
  }

  static getTableColumns(tableName: string): string {
    return `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TABLE_COLUMNS(tableName)}`;
  }

  static getTableRelations(tableName: string): string {
    return `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TABLE_RELATIONS(tableName)}`;
  }

  static getTransitiveRelations(tableName: string, usedTables?: string): string {
    const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TRANSITIVE_RELATIONS(tableName)}`;
    return usedTables ? `${url}?used_tables=${usedTables}` : url;
  }

  static getTransitiveRelationsWithJoins(tableName: string): string {
    return `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TRANSITIVE_RELATIONS_WITH_JOINS(tableName)}`;
  }

  static getForeignKeys(sourceTable: string, targetTable: string): string {
    return `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.FOREIGN_KEYS(sourceTable, targetTable)}`;
  }

  static getJoinedColumns(): string {
    return `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.JOINED_COLUMNS}`;
  }

  static getReport(): string {
    return `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.REPORT}`;
  }

  static getAvailableFunctions(): string {
    return `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.FUNCTIONS}`;
  }
}
