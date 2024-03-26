import './base.cy'

describe('Bad domain names', () => {
  it('accepts valid domain names', () => {
    cy.goToDomain()
    cy.get('#id_domain_name').type('dosac')
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Has a central government minister requested the dosac.gov.uk domain name?')
  })

  it('accepts valid domain names with hyphens', () => {
    cy.goToDomain()
    cy.get('#id_domain_name').type('dos-ac')
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Has a central government minister requested the dos-ac.gov.uk domain name?')
  })

  it('accepts valid domain names when user has entered .gov.uk', () => {
    cy.goToDomain()
    cy.get('#id_domain_name').type('dosac.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Has a central government minister requested the dosac.gov.uk domain name?')
  })

  it('rejects invalid domain names', () => {
    cy.goToDomain()
    cy.get('#id_domain_name').clear().type('dos.ac')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')

    cy.get('#id_domain_name').clear().type('dos.ac.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')

    cy.get('#id_domain_name').clear().type('DoSAC.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')

    cy.get('#id_domain_name').clear().type('007.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')

    cy.get('#id_domain_name').clear().type('-blah.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')

    cy.get('#id_domain_name').clear().type('blah-.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')

    cy.get('#id_domain_name').clear().type('b.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')
  })

  it('rejects bad domain names but accepts valid retry', () => {
    cy.goToDomain()
    cy.get('#id_domain_name').clear().type('DoSAC.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h2').should('include.text', 'There is a problem')
    cy.get('#id_domain_name').clear().type('dosac.gov.uk')
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Has a central government minister requested the dosac.gov.uk domain name?')
  })

})
