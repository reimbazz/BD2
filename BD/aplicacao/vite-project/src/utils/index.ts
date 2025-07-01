import type { Attribute, FilterOperator, AggregateFunction, OrderBy, Filter } from '../types';

/**
 * Utilitários para manipulação de atributos
 */
export class AttributeUtils {
  /**
   * Obtém o nome qualificado de um atributo (table.column ou column)
   */
  static getQualifiedName(attr: Attribute): string {
    return attr.qualified_name || attr.name;
  }

  /**
   * Mapeia atributos para formato de opções do v-select
   */
  static mapToSelectItems(attributes: Attribute[]) {
    return attributes.map(attr => ({
      title: this.getQualifiedName(attr),
      value: this.getQualifiedName(attr),
      type: attr.type,
      table: attr.table
    }));
  }

  /**
   * Filtra atributos disponíveis baseado em uma lista de nomes selecionados
   */
  static filterAvailableAttributes(
    allAttributes: Attribute[], 
    selectedNames: string[]
  ): Attribute[] {
    return allAttributes.filter(attr =>
      selectedNames.includes(this.getQualifiedName(attr))
    );
  }

  /**
   * Adiciona qualificação de tabela aos atributos
   */
  static addTableQualification(attributes: { name: string; type: string }[], tableName: string): Attribute[] {
    return attributes.map(attr => ({
      ...attr,
      table: tableName,
      qualified_name: `${tableName}.${attr.name}`
    }));
  }
}

/**
 * Utilitários para operadores de filtro
 */
export class FilterUtils {
  private static readonly NUMERIC_OPERATORS: Array<{ title: string; value: FilterOperator }> = [
    { title: 'Igual (=)', value: '=' },
    { title: 'Diferente (≠)', value: '!=' },
    { title: 'Maior que (>)', value: '>' },
    { title: 'Menor que (<)', value: '<' },
    { title: 'Maior ou igual (≥)', value: '>=' },
    { title: 'Menor ou igual (≤)', value: '<=' },
    { title: 'Em lista (IN)', value: 'IN' },
    { title: 'Não em lista (NOT IN)', value: 'NOT IN' }
  ];

  private static readonly TEXT_OPERATORS: Array<{ title: string; value: FilterOperator }> = [
    { title: 'Igual (=)', value: '=' },
    { title: 'Diferente (≠)', value: '!=' },
    { title: 'Como (LIKE)', value: 'LIKE' },
    { title: 'Como (sem case)', value: 'ILIKE' },
    { title: 'Em lista (IN)', value: 'IN' },
    { title: 'Não em lista (NOT IN)', value: 'NOT IN' }
  ];

  private static readonly DATE_OPERATORS: Array<{ title: string; value: FilterOperator }> = [
    { title: 'Igual (=)', value: '=' },
    { title: 'Diferente (≠)', value: '!=' },
    { title: 'Depois de (>)', value: '>' },
    { title: 'Antes de (<)', value: '<' },
    { title: 'A partir de (≥)', value: '>=' },
    { title: 'Até (≤)', value: '<=' }
  ];

  private static readonly DEFAULT_OPERATORS: Array<{ title: string; value: FilterOperator }> = [
    { title: 'Igual (=)', value: '=' },
    { title: 'Diferente (≠)', value: '!=' },
    { title: 'Em lista (IN)', value: 'IN' },
    { title: 'Não em lista (NOT IN)', value: 'NOT IN' }
  ];

  /**
   * Retorna operadores disponíveis baseado no tipo de dados
   */
  static getAvailableOperators(dataType: string): Array<{ title: string; value: FilterOperator }> {
    const type = dataType.toLowerCase();
    
    if (this.isNumericType(type)) {
      return this.NUMERIC_OPERATORS;
    }
    
    if (this.isTextType(type)) {
      return this.TEXT_OPERATORS;
    }
    
    if (this.isDateType(type)) {
      return this.DATE_OPERATORS;
    }
    
    return this.DEFAULT_OPERATORS;
  }

  /**
   * Verifica se é um operador de lista (IN, NOT IN)
   */
  static isListOperator(operator: string): boolean {
    return ['IN', 'NOT IN'].includes(operator);
  }

  /**
   * Verifica se é um tipo numérico
   */
  static isNumericType(type: string): boolean {
    return type.includes('int') || 
           type.includes('float') || 
           type.includes('decimal') || 
           type.includes('numeric') ||
           type.includes('double precision');
  }

  /**
   * Verifica se é um tipo de texto
   */
  static isTextType(type: string): boolean {
    return type.includes('char') || 
           type.includes('text') || 
           type.includes('varchar');
  }

  /**
   * Verifica se é um tipo de data
   */
  static isDateType(type: string): boolean {
    return type.includes('date') || type.includes('time');
  }

  /**
   * Obtém o tipo de input baseado no tipo de dados
   */
  static getInputType(dataType: string): string {
    const type = dataType.toLowerCase();
    
    if (this.isNumericType(type)) {
      return 'number';
    }
    
    if (this.isDateType(type)) {
      return 'date';
    }
    
    return 'text';
  }

  /**
   * Obtém placeholder apropriado para o operador
   */
  static getPlaceholder(operator: string): string {
    if (operator === 'LIKE' || operator === 'ILIKE') {
      return 'Use % para wildcards (ex: %texto%)';
    }
    
    if (this.isListOperator(operator)) {
      return 'valor1, valor2, valor3...';
    }
    
    return 'Digite o valor';
  }
}

/**
 * Utilitários para validação
 */
export class ValidationUtils {
  /**
   * Valida se uma configuração de relatório está completa
   */
  static validateReportConfig(config: {
    selectedTable: string;
    selectedAttributes: string[];
  }): { isValid: boolean; message?: string } {
    if (!config.selectedTable) {
      return { isValid: false, message: 'Selecione uma tabela base' };
    }

    if (config.selectedAttributes.length === 0) {
      return { isValid: false, message: 'Selecione pelo menos um atributo' };
    }

    return { isValid: true };
  }

  /**
   * Valida se uma configuração de join está completa
   */
  static validateJoinConfig(join: {
    targetTable: string;
    sourceAttribute: string;
    targetAttribute: string;
  }): boolean {
    return Boolean(join.targetTable && join.sourceAttribute && join.targetAttribute);
  }
}

/**
 * Utilitários para formatação de dados
 */
export class FormatUtils {
  /**
   * Formata uma função de agregação para exibição
   */
  static formatAggregateFunction(func: { function: string; attribute: string; alias?: string }): string {
    const base = `${func.function}(${func.attribute})`;
    return func.alias ? `${base} AS ${func.alias}` : base;
  }

  /**
   * Formata uma configuração de ordenação para exibição
   */
  static formatOrderBy(order: { attribute: string; direction: string }, index: number): string {
    return `${index + 1}. ${order.attribute} ${order.direction}`;
  }

  /**
   * Formata uma configuração de join para exibição
   */
  static formatJoin(join: { sourceAttribute: string; joinType: string; targetAttribute: string }): string {
    return `${join.sourceAttribute} ${join.joinType} ${join.targetAttribute}`;
  }
}

/**
 * Utilitários para funções de agregação
 */
export class AggregateUtils {
  /**
   * Cria uma função de agregação padrão
   */
  static createDefault(): AggregateFunction {
    return {
      function: "COUNT",
      attribute: "",
      alias: "",
    };
  }

  /**
   * Valida se uma função de agregação está completa
   */
  static validate(aggregate: AggregateFunction): boolean {
    return !!(aggregate.function && aggregate.attribute);
  }

  /**
   * Gera um alias automático para uma função de agregação
   */
  static generateAlias(aggregate: AggregateFunction): string {
    return aggregate.alias || `${aggregate.function}_${aggregate.attribute.replace('.', '_')}`;
  }

  /**
   * Obtém funções disponíveis baseado no tipo do atributo
   */
  static getAvailableFunctions(attributeType: string): string[] {
    const type = attributeType.toLowerCase();
    
    if (["integer", "bigint", "double precision", "numeric"].includes(type)) {
      return ["COUNT", "SUM", "AVG", "MIN", "MAX"];
    }
    
    if (["varchar", "char", "text"].some(t => type.includes(t))) {
      return ["COUNT"];
    }
    
    return ["COUNT"];
  }
}

/**
 * Utilitários para ordenação
 */
export class OrderByUtils {
  /**
   * Cria uma ordenação padrão
   */
  static createDefault(): OrderBy {
    return {
      attribute: '',
      direction: 'ASC'
    };
  }

  /**
   * Converte formato de ordenação para compatibilidade com backend
   */
  static convertFormat(order: OrderBy) {
    return {
      column: order.attribute,
      direction: order.direction
    };
  }
}

/**
 * Utilitários para tipos de dados
 */
export class TypeUtils {
  /**
   * Mapeia tipo SQL para categoria básica
   */
  static getAttributeType(attr: Attribute): 'number' | 'string' | 'date' | 'unknown' {
    const type = attr.type.toLowerCase();
    
    if (["integer", "bigint", "double precision", "numeric", "decimal"].includes(type)) {
      return "number";
    }
    
    if (["varchar", "char", "text"].some(t => type.includes(t))) {
      return "string";
    }
    
    if (["timestamp", "date", "datetime"].some(t => type.includes(t))) {
      return "date";
    }
    
    return "unknown";
  }
}
