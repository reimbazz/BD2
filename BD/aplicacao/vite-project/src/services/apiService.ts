import axios from 'axios';
import { ApiUrlBuilder } from '../config/api';
import type { 
  Attribute, 
  Join, 
  ReportRequest, 
  ReportResponse, 
  TableRelations, 
  ApiResponse 
} from '../types';

/**
 * Serviço centralizado para comunicação com a API
 */
export class ApiService {
  /**
   * Busca todas as tabelas disponíveis
   */
  static async getTables(): Promise<string[]> {
    try {
      const response = await axios.get<ApiResponse<string[]>>(ApiUrlBuilder.getTables());
      return response.data.tables || [];
    } catch (error) {
      console.error('Erro ao buscar tabelas:', error);
      throw new Error('Erro ao carregar tabelas. Tente novamente mais tarde.');
    }
  }

  /**
   * Busca colunas de uma tabela específica
   */
  static async getTableColumns(tableName: string): Promise<Attribute[]> {
    try {
      const response = await axios.get<ApiResponse<Attribute[]>>(
        ApiUrlBuilder.getTableColumns(tableName)
      );
      return response.data.columns || [];
    } catch (error) {
      console.error(`Erro ao carregar colunas da tabela ${tableName}:`, error);
      throw new Error(`Erro ao carregar colunas da tabela ${tableName}.`);
    }
  }

  /**
   * Busca relações transitivas de uma tabela
   */
  static async getTransitiveRelations(tableName: string, usedTables?: string[]): Promise<TableRelations> {
    try {
      const usedTablesParam = usedTables?.join(',') || '';
      const response = await axios.get<ApiResponse<TableRelations>>(
        ApiUrlBuilder.getTransitiveRelations(tableName, usedTablesParam)
      );
      return response.data.relations || { direct: [], transitive: {} };
    } catch (error) {
      console.error(`Erro ao buscar relações transitivas da tabela ${tableName}:`, error);
      throw new Error(`Erro ao carregar relações da tabela ${tableName}.`);
    }
  }

  /**
   * Busca relações transitivas considerando joins existentes
   */
  static async getTransitiveRelationsWithJoins(
    baseTable: string, 
    joins: Join[]
  ): Promise<TableRelations> {
    try {
      const response = await axios.post<ApiResponse<TableRelations>>(
        ApiUrlBuilder.getTransitiveRelationsWithJoins(baseTable),
        { baseTable, joins }
      );
      return response.data.relations || { direct: [], transitive: {} };
    } catch (error) {
      console.error(`Erro ao buscar relações transitivas com joins para ${baseTable}:`, error);
      throw new Error(`Erro ao carregar relações transitivas com joins.`);
    }
  }

  /**
   * Busca colunas de tabelas joinadas
   */
  static async getJoinedTablesColumns(baseTable: string, joins: Join[]): Promise<Attribute[]> {
    try {
      const response = await axios.post<ApiResponse<Attribute[]>>(
        ApiUrlBuilder.getJoinedColumns(),
        { baseTable, joins }
      );
      return response.data.columns || [];
    } catch (error) {
      console.error('Erro ao carregar colunas das tabelas joinadas:', error);
      throw new Error('Erro ao carregar atributos das tabelas joinadas.');
    }
  }

  /**
   * Busca relações de chave estrangeira entre duas tabelas
   */
  static async getForeignKeyRelations(
    sourceTable: string, 
    targetTable: string
  ): Promise<Array<{ source_column: string; target_column: string }>> {
    try {
      const response = await axios.get<ApiResponse<Array<{ source_column: string; target_column: string }>>>(
        ApiUrlBuilder.getForeignKeys(sourceTable, targetTable)
      );
      return response.data.relations || [];
    } catch (error) {
      console.error(`Erro ao buscar relações FK entre ${sourceTable} e ${targetTable}:`, error);
      return []; // Retorna array vazio em caso de erro ao invés de lançar exceção
    }
  }

  /**
   * Gera relatório ADHOC
   */
  static async generateReport(request: ReportRequest): Promise<ReportResponse> {
    try {
      const response = await axios.post<ReportResponse>(
        ApiUrlBuilder.getReport(),
        request
      );
      return response.data;
    } catch (error) {
      console.error('Erro ao gerar relatório:', error);
      
      let errorMessage = 'Erro ao gerar relatório.';
      if (axios.isAxiosError(error) && error.response?.data?.detail) {
        errorMessage += ' ' + error.response.data.detail;
      } else if (error instanceof Error) {
        errorMessage += ' ' + error.message;
      }
      
      throw new Error(errorMessage);
    }
  }

  /**
   * Busca funções disponíveis por tipo de dados
   */
  static async getAvailableFunctions(): Promise<Record<string, Array<{ value: string; label: string }>>> {
    try {
      const response = await axios.get<ApiResponse<Record<string, Array<{ value: string; label: string }>>>>(
        ApiUrlBuilder.getAvailableFunctions()
      );
      return response.data.functions || {};
    } catch (error) {
      console.error('Erro ao buscar funções disponíveis:', error);
      throw new Error('Erro ao carregar funções disponíveis.');
    }
  }
}
