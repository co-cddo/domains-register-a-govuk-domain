import './base.cy'

describe('Bad domain names', () => {
  it('accepts valid domain names', () => {
    cy.goToDomain('')
    cy.get('#id_domain_name').type('dosac')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h1').should('include.text', 'Has a central government minister requested the domain name?')
  })

  it('accepts valid domain names with hyphens', () => {
    cy.goToDomain('')
    cy.get('#id_domain_name').type('dos-ac')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h1').should('include.text', 'Has a central government minister requested the domain name?')
  })

  it('accepts valid domain names when user has entered .gov.uk', () => {
    cy.goToDomain('')
    cy.get('#id_domain_name').type('dosac.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h1').should('include.text', 'Has a central government minister requested the domain name?')
  })

  it('rejects domain names with dots', () => {
    cy.goToDomain('')
    cy.get('#id_domain_name').type('dos.ac')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')
  })

  it('rejects domain names with dots and .gov.uk', () => {
    cy.goToDomain('')
    cy.get('#id_domain_name').type('dos.ac.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')
  })

  it('rejects domain names with invalid chars', () => {
    cy.goToDomain('')
    cy.get('#id_domain_name').type('DoSAC.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')
  })

  it('rejects domain names that starts with numbers', () => {
    cy.goToDomain('')
    cy.get('#id_domain_name').type('007.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')
  })

  it('rejects domain names with hyphen at the start', () => {
    cy.goToDomain('')
    cy.get('#id_domain_name').type('-blah.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')
  })

  it('rejects domain names with hyphen at the end', () => {
    cy.goToDomain('')
    cy.get('#id_domain_name').type('blah-.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')
  })

  it('rejects domain names with a single letter', () => {
    cy.goToDomain('')
    cy.get('#id_domain_name').type('b.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')
  })

  it('rejects bad domain names but accepts valid retry', () => {
    cy.goToDomain('')
    cy.get('#id_domain_name').type('DoSAC.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')
    cy.get('#id_domain_name').clear().type('dosac.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h1').should('include.text', 'Has a central government minister requested the domain name?')
  })

})
