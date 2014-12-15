package basic

import com.excilys.ebi.gatling.core.Predef._
import com.excilys.ebi.gatling.http.Predef._
import com.excilys.ebi.gatling.jdbc.Predef._
import com.excilys.ebi.gatling.http.Headers.Names._
import akka.util.duration._
import bootstrap._
import scala.collection.mutable.ArrayBuffer
import com.excilys.ebi.gatling.core.structure.ScenarioBuilder
import scala.sys.process._
import java.util.Calendar

class Perf extends Simulation {

 
  //la duree du test en seconde
  val dureeTest = 60

  /******************************************************************/
  /******************************************************************/
  /***************************   HTTPCONF   **************************/
  /******************************************************************/
  /******************************************************************/
  /******************************************************************/

  val baseUrl = httpConfig
    .baseURL("localhost:5000/stock/")

 
  /******************************************************************/
  /******************************************************************/
  /***************************   FEEDS   ****************************/
  /******************************************************************/
  /******************************************************************/
  /******************************************************************/

  // TODO produire les fichiers de feeds
  val feedImeiPsav = csv("imeiPsav.csv").random // imei,gencod,psav
  val feedImeiPsavPersistent = csv("imeiPsavPersistent.csv").random // imei,gencod,psav, que les psav qui ne servent pas au transfert de stock
  val feedPsav = csv("psav.csv").random 
  val feedPsavTransfert = csv("psavTransfert.csv").random

  val feedEtat = new Feeder[String] {

    private val RNG = new scala.util.Random

    override def hasNext = true

    override def next: Map[String, String] = {
      val rand: Int = RNG.nextInt(1)
      var etat = "D"
      if (rand == 1) {
        etat = "K"
      }
      Map("etat" -> etat)
    }
  }

  val feedBodyStock = new Feeder[String] {
    //TODO
  }
 
  //fin feeds

  /******************************************************************/
  /******************************************************************/
  /**********************    SCENARIO    ****************************/
  /******************************************************************/
  /******************************************************************/

  //les scenarios

  val scnBulkCheckImei = scenario("Interrogation en masse")
    .feed(feedPSAV)
    .exec(
      http("Interrogation en masse")
        .get("/${psav}/")
        .check(status.is(200)))

  val scnCheckImei = scenario("Check d'un imei")
    .feed(feedImeiPsav)
    .exec(
      http("Check d'un imei")
        .get("/${psav}/imei/${imei}")
        .check(status.in(200,404)))

  val scnUpdateImei = scenario("Changement d'état d'un imei")
    .feed(feedImeiPsavPersistent)
    .feed(feedEtat)
    .exec(
      http("Changement d'état d'un imei")
        .put("/${psav}/imei/${imei}?etat=${etat}")
        .check(status.is(204)))

  val scnInsertImei = scenario("Insertion en stock")
    .feed(feedPSAV)
    .feed(feedBodyStock)
    .exec( // voir comment on fait une boucle
      http("Insertion en stock")
        .post("/${psav}/imei")
        .body("${bodystock}").asJSON()
        .check(status.is(201)))

  val scnTransfertActivite = scenario("Transfert activité")
    .feed(feedPsavTransfert)
    .feed(feedPsav)
    .exec(
      http("Transfert activité")
        .post("/${psavTransfert}/transfert/${psav}")
        .check(status.is(200)))

  val scnReappro = scenario("Réapprovisionnement")
    .exec(
      http("Réapprovisionnement")
        .post("/reappro")
        .check(status.is(200)))
 //fin scenario   

  /******************************************************************/
  /******************************************************************/
  /**********************    LANCEMENT    ***************************/
  /******************************************************************/
  /******************************************************************/

  //lancement des tests
  val nbBulkCheckParSeconde = ??
  val nbCheckImeiParSeconde = ??
  val nbUpdateImeiParSeconde = ??
  val nbInsertImeiParSeconde = ??
  val nbTransfertParSeconde = ??
  val nbReapproParSeconde = ??
  
  setUp(scnBulkCheckImei.users(dureeTest * nbBulkCheckParSeconde).ramp(dureeTest).protocolConfig(baseUrl))
  setUp(scnCheckImei.users(dureeTest * nbCheckImeiParSeconde).ramp(dureeTest).protocolConfig(baseUrl))
  setUp(scnUpdateImei.users(dureeTest * nbUpdateImeiParSeconde).ramp(dureeTest).protocolConfig(baseUrl))
  setUp(scnInsertImei.users(dureeTest * nbInsertImeiParSeconde).ramp(dureeTest).protocolConfig(baseUrl))
  setUp(scnTransfertActivite.users(dureeTest * nbTransfertParSeconde).ramp(dureeTest).protocolConfig(baseUrl))
  setUp(scnReappro.users(dureeTest * nbReapproParSeconde).ramp(dureeTest).protocolConfig(baseUrl))

// Revoir les deux derniers cas
  //setUp(
  //scn.inject(
  //  nothingFor(4 seconds), // 1
  //  atOnceUsers(10), // 2
  //  rampUsers(10) over(5 seconds), // 3
  //  constantUsersPerSec(20) during(15 seconds), // 4
  //  constantUsersPerSec(20) during(15 seconds) randomized, // 5
  //  rampUsersPerSec(10) to(20) during(10 minutes), // 6
  //  rampUsersPerSec(10) to(20) during(10 minutes) randomized, // 7
  //  splitUsers(1000) into(rampUsers(10) over(10 seconds)) separatedBy(10 seconds), // 8
  //  splitUsers(1000) into(rampUsers(10) over(10 seconds)) separatedBy(atOnceUsers(30)), // 9
  //  heavisideUsers(1000) over(20 seconds) // 10
  //  ).protocols(httpConf)
  //)

}

