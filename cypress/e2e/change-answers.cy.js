import './base.cy'

describe('Changing answers at the end of the process', () => {


  it('lets you change your answer about whether you have minister approval', () => {
    cy.goToConfirmation(7)
    cy.get("a[href='/minister']").eq(0).click()
    cy.checkPageTitleIncludes('Has a central government minister requested')
    cy.get('input[type=radio]').eq(0).should('be.checked')

    // No going back to answers
    cy.get('#id_back_to_answers').should('not.exist')

    // change the answer
    cy.selectYesOrNo('minister', 'no')

    // and see the new page
    cy.checkPageTitleIncludes('Registrant details')
  })


  it('lets you change your answer about whether you have permission', () => {
    cy.goToConfirmation(7)
    cy.get("a[href='/written-permission']").eq(0).click()
    cy.checkPageTitleIncludes('Does your registrant have proof of permission')
    cy.get('input[type=radio]').eq(0).should('be.checked')

    // No going back to answers
    cy.get('#id_back_to_answers').should('not.exist')

    // change the answer
    cy.selectYesOrNo('written_permission', 'no')

    // and fail
    cy.checkPageTitleIncludes('Your registrant does not have the evidence required to get a .gov.uk domain name')
  })


  it('lets you change your answer about whether you have an exemption', () => {
    cy.goToConfirmation(7)
    cy.get("a[href='/exemption']").eq(0).click()
    cy.checkPageTitleIncludes('Does your registrant have an exemption')
    cy.get('input[type=radio]').eq(0).should('be.checked')

    // No going back to answers
    cy.get('#id_back_to_answers').should('not.exist')

    // change the answer
    cy.selectYesOrNo('exemption', 'no')

    // and fail
    cy.checkPageTitleIncludes('Your registrant cannot get approval for a .gov.uk domain name')
  })


  it('lets you change various details', () => {
    cy.goToConfirmation()
    cy.get("a[href='/change-registrar-details']").eq(0).click()
    cy.checkPageTitleIncludes('Registrar details')

    // check previously entered registrar details are pre-filled
    cy.get('#id_registrar_organisation').should('have.value', 'WeRegister')
    cy.get('#id_registrar_name').should('have.value', 'Joe Bloggs')
    cy.get('#id_registrar_phone').should('have.value', '01225672345')
    cy.get('#id_registrar_email').should('have.value', 'joe@example.org')

    // change a value
    cy.get('#id_registrar_phone').clear().type('01225672345')

    // go back to answers
    cy.get('#id_back_to_answers').click()
    cy.checkPageTitleIncludes('Check your answers')
    cy.summaryShouldHave(1, '01225672345')

    // change a value to something wrong then correct it
    cy.get("a[href='/change-registrant-details']").eq(0).click()
    cy.checkPageTitleIncludes('Registrant details')
    cy.get('#id_registrant_phone').clear().type('2384')
    cy.get('#id_back_to_answers').click()
    cy.checkPageTitleIncludes('Registrant details')
    cy.confirmProblem('Please enter a valid phone number')
    cy.get('#id_registrant_phone').clear().type('01233456876')
    cy.get('#id_back_to_answers').click()
    cy.checkPageTitleIncludes('Check your answers')
    cy.summaryShouldHave(5, '01233456876')
  })


  it('doesn\'t let you come back to answers if you change the registrant type', () => {
    cy.goToConfirmation()
    cy.get("a[href='/registrant-type']").eq(0).click()
    cy.checkPageTitleIncludes('Who is this domain name for?')
    // check if value is pre-selected with the previous choice
    cy.get('input[type=radio]').eq(2).should('be.checked')

    // No going back to answers
    cy.get('#id_back_to_answers').should('not.exist')

    // Change route and check if we go to the expected new route
    cy.chooseRegistrantType(1) // Central government -> Route 2
    cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')
  })


})
